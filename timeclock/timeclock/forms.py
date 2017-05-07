from timepiece.entries.forms import ClockOutForm

from django import forms

from timeclock.models import TaskList


class ClockOutFormWithTasks(ClockOutForm):
    task_list = forms.CharField(label='Tasks done today', widget=forms.Textarea,
                                required=True)

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = kwargs.get('initial', None) or {}
        super(ClockOutFormWithTasks, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        entry = super(ClockOutFormWithTasks, self).save(commit=commit)
        if self.cleaned_data['task_list']:
            TaskList.objects.update_or_create(
                entry=entry, defaults={'tasks': self.cleaned_data['task_list']})
        return entry
