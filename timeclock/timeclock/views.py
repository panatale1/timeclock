import datetime
from dateutil.relativedelta import relativedelta

from six.moves.urllib.parse import urlencode

from timepiece.crm.utils import grouped_totals
from timepiece.crm.views import ProjectTimesheet, ProjectTimesheetCSV, ListUsers
from timepiece.entries.forms import ClockInForm
from timepiece.entries.models import Entry, ProjectHours
from timepiece.entries.views import Dashboard
from timepiece.forms import YearMonthForm, UserYearMonthForm
from timepiece.utils import get_active_entry, get_week_start, add_timezone, get_month_start
from timepiece.utils.csv import CSVViewMixin
from timepiece.utils.views import cbv_decorator

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models.aggregates import Sum
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView

from timeclock.forms import ClockOutFormWithTasks
from timeclock.models import TaskList

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return HttpResponseRedirect(reverse('dashboard'))
        if not request.user.timepiece_entries.all().exists():
            return HttpResponseRedirect(reverse('clock_in'))
        entry = request.user.timepiece_entries.first()
        if entry and entry.end_time:
            return HttpResponseRedirect(reverse('clock_in'))
        else:
            return HttpResponseRedirect(reverse('clock_out'))


class CustomDashboard(Dashboard):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        today, week_start, week_end = self.get_dates()

        active_entry = get_active_entry(self.user)
        week_entries = week_entries = Entry.objects.filter(
            user=self.user).select_related('project', 'tasks')
        assignments = ProjectHours.objects.filter(
                user=self.user, week_start=week_start.date())
        project_progress = self.process_progress(week_entries, assignments)
        others_active_entries = Entry.objects.filter(
                end_time__isnull=True).exclude(user=self.user).select_related(
                'user', 'project', 'activity')
        return {
            'active_tab': self.active_tab,
            'today': today,
            'week_start': week_start.date(),
            'week_end': week_end.date(),
            'active_entry': active_entry,
            'week_entries': week_entries,
            'project_progress': project_progress,
            'others_active_entries': others_active_entries
        }


@permission_required('entries.can_clock_in')
@transaction.atomic
def clock_in(request):
    """This uses the same logic as timepiece.entries.views.clock_in,
       but requires a different template"""

    user = request.user
    active_entry = get_active_entry(user, select_for_update=True)

    initial = dict([(k, v) for k, v in request.GET.items()])
    data = request.POST or None
    form = ClockInForm(data, initial=initial, user=user, active=active_entry)
    if form.is_valid():
        entry = form.save()
        message = 'You have clocked into {0} on {1}'.format(
            entry.activity.name, entry.project)
        messages.info(request, message)
        return HttpResponseRedirect(reverse('dashboard'))
    return render(request, 'entry/clock_in.html', {
        'form': form,
        'active': active_entry
    })


@permission_required('entries.can_clock_out')
def clock_out(request):
    """Like clock_in, needs new template, as well as new form"""
    entry = get_active_entry(request.user)
    if not entry:
        message = "Not clocked in"
        messages.info(request, message)
        return HttpresponseRedirect(reverse('dashboard'))
    if request.POST:
        form = ClockOutFormWithTasks(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()
            message = 'You have clocked out of {0} on {1}'.format(
                entry.activity.name, entry.project)
            messages.info(request, message)
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            message = 'Please correct the errors below.'
            messages.error(request, message)
    else:
        form = ClockOutFormWithTasks(instance=entry)
    return render(request, 'entry/clock_out.html', {
        'form': form,
        'entry': entry,
    })


@login_required
def view_user_timesheet(request, user_id, active_tab):
    user = get_object_or_404(User, pk=user_id)
    has_perm = request.user.has_perm('entries.view_entry_summary')
    if not (has_perm or user.pk == request.user.pk):
        return HttpResponseForbidden('Forbidden')

    FormClass = UserYearMonthForm if has_perm else YearMonthForm
    form = FormClass(request.GET or None)
    if form.is_valid():
        if has_perm:
            from_date, to_date, form_user = form.save()
            if form_user and request.GET.get('yearmonth', None):
                url = reverse('view_user_timesheet', args=(form_user.pk, ))
                request_data = {
                    'month': from_date.month,
                    'year': from_date.year,
                    'user': form_user.pk,
                }
                url += '?{0}'.format(urlencode(request_data))
                return HttpResponseRedirect(url)
        else:
            from_date, to_date = form.save()
        from_date = add_timezone(from_date)
        to_date = add_timezone(to_date)
    else:
        # from_date = get_month_start()
        # to_date = from_date + relativedelta(months=1)
        from_date = Entry.objects.last().start_time
        to_date = datetime.datetime.today()

    entries_qs = Entry.objects.filter(user=user)
    if form.is_valid():
        month_qs = entries_qs.timespan(from_date, span='month')
    else:
        month_qs = entries_qs.timespan(from_date)
    extra_values = (
        'start_time', 'end_time', 'comments', 'seconds_paused', 'id', 'location__name',
        'project__name', 'activity__name', 'status')
    month_entries = month_qs.date_trunc('month', extra_values).order_by('start_time')
    entry_ids = month_entries.values_list('id', flat=True)
    tasks = TaskList.objects.filter(entry_id__in=entry_ids).values(
        'entry_id', 'tasks').order_by('entry_id')
    task_values = [
        tasks.get(entry_id=entry_id)['tasks']
        if entry_id in tasks.values_list('entry_id', flat=True)
        else ''
        for entry_id in entry_ids
    ]
    first_week = get_week_start(from_date)
    month_week = first_week + relativedelta(weeks=1)
    grouped_qs = entries_qs.timespan(first_week, to_date=to_date)
    intersection = grouped_qs.filter(start_time__lt=month_week, start_time__gte=from_date)
    if not intersection and first_week.month < from_date.month:
        grouped_qs = entries_qs.timespan(from_date, to_date=to_date)
    totals = grouped_totals(grouped_qs) if month_entries else ''
    project_entries = month_qs.order_by().values(
        'project__name').annotate(sum=Sum('hours')).order_by('-sum')
    summary = Entry.summary(user, from_date, to_date)

    show_approve = show_verify = False
    can_change = request.user.has_perm('entries.can_change_entry')
    can_approve = request.user.has_perm('entries.approve_timesheet')
    if can_change or can_approve or user == request.user:
        statuses = list(month_qs.values_list('status', flat=True))
        total_statuses = len(statuses)
        unverified_count = statuses.count(Entry.UNVERIFIED)
        verified_count = statuses.count(Entry.VERIFIED)
        approved_count = statuses.count(Entry.APPROVED)
    if can_change or user == request.user:
        show_verify = unverified_count != 0
    if can_approve:
        show_approve = all([
            verified_count + approved_count == total_statuses,
            verified_count > 0,
            total_statuses != 0,
        ])

        return render(request, 'user/timesheet_view.html', {
            'active_tab': active_tab or 'overview',
            'year_month_form': form,
            'from_date': from_date,
            'to_date': to_date - relativedelta(days=1),
            'show_verify': show_verify,
            'show_approve': show_approve,
            'timesheet_user': user,
            'entries': zip(month_entries, task_values),
            'grouped_totals': totals,
            'project_entries': project_entries,
            'summary': summary
        })


@cbv_decorator(permission_required('entries.view_project_timesheet'))
class UpdatedProjectTimesheet(ProjectTimesheet):
    template_name = 'project/timesheet.html'

    def get_context_data(self, **kwargs):
        context = super(UpdatedProjectTimesheet, self).get_context_data(**kwargs)
        entries = context['entries']
        entry_ids = entries.values_list('id', flat=True)
        tasks = TaskList.objects.filter(
            entry_id__in=entry_ids
        ).values('entry_id', 'tasks').order_by('entry_id')
        task_values = [
            tasks.get(entry_id=entry_id)['tasks'] if
            entry_id in tasks.values_list('entry_id', flat=True)
            else ''
            for entry_id in entry_ids ]
        for i in range(entries.count()):
            entries[i]['tasks'] = task_values[i]
        return context


class UpdatedProjectTimesheetCSV(CSVViewMixin, UpdatedProjectTimesheet):

    def get_filename(self, context):
        project = self.object.name
        to_date_str = context['to_date'].strftime('%m-%d-%Y')
        return 'Project_timesheet {0} {1}'.format(project, to_date_str)

    def convert_context_to_csv(self, context):
        rows = []
        rows.append([
            'Date',
            'User',
            'Activity',
            'Time In',
            'Time Out',
            'Hours',
            'Comments',
            'Tasks'
        ])
        for entry in context['entries']:
            data = [
                entry['start_time'].strftime('%x'),
                entry['user__first_name'] + ' ' + entry['user__last_name'],
                entry['activity__name'],
                entry['start_time'].strftime('%X'),
                entry['end_time'].strftime('%X'),
                entry['hours'],
                entry['comments'],
                entry['tasks'],
            ]
            rows.append(data)
        total = context['total']
        rows.append(('', '', '', '', 'Total:', total))
        return rows


class ListUsersAlpha(ListUsers):

    def get_queryset(self):
        return super(ListUsersAlpha, self).get_queryset().order_by('last_name')
