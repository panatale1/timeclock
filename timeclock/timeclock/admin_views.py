from django.views.generic import TemplateView


class VolunteerReport(TemplateView):
    template_name='admin/reports/report.html'


class HourlyReport(TemplateView):
    template_name='admin/reports/report.html'
