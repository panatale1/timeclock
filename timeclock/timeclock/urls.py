from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from .admin_views import HourlyReport, VolunteerReport
from .views import (ProfileView, CustomDashboard, clock_in, clock_out, ListUsersAlpha,
                    view_user_timesheet, UpdatedProjectTimesheet, UpdatedProjectTimesheetCSV)

urlpatterns = [
    # Examples:
    # url(r'^$', 'timeclock.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^dashboard/(?:(?P<active_tab>progress|all-entries|online-users)/)?$',
        CustomDashboard.as_view(), name='dashboard'),
    url(r'^user/(?P<user_id>\d+)/timesheet/(?:(?P<active_tab>overview|all-entries|daily-summary)/)?$',
        view_user_timesheet, name='view_user_timesheet'),
    url(r'^entry/clock_in/$', clock_in, name='clock_in'),
    url(r'^entry/clock_out/$', clock_out, name='clock_out'),
    url(r'project/(?P<project_id>\d+)/timesheet/$',
        UpdatedProjectTimesheet.as_view(), name='view_project_timesheet'),
    url(r'^project/(?P<project_id>\d+)/timesheet/csv/$',
        UpdatedProjectTimesheetCSV.as_view(), name='view_project_timesheet_csv'),
    url(r'^user/$', ListUsersAlpha.as_view(), name='list_users'),
    url(r'^', include('timepiece.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='auth_login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='auth_logout'),
    url(r'^accounts/password-change/$', 'django.contrib.auth.views.password_change',
        name='change_password'),
    url(r'^accounts/password-change/done/$', 'django.contrib.auth.views.password_change_done'),
    url(r'^accounts/password-reset/$', 'django.contrib.auth.views.password_reset',
        name='reset_password'),
    url(r'^accounts/password-reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/%',
        'django.contrib.auth.views.password_reset_confirm'),
    url(r'^accounts/profile/$', ProfileView.as_view(), name='profile'),
    url(r'^accounts/reset/done', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^dash/', include([
        url(r'^volunteer-report/$', VolunteerReport.as_view(), name='volunteer-report'),
        url(r'^hours-report/$', HourlyReport.as_view(), name='hours-report'),
    ])),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns .insert(0, url(r'^__debug__/', include(debug_toolbar.urls)))
