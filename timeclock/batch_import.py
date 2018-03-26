from csv import reader
from datetime import datetime

from django.contrib.auth.models import User, Group

from timepiece.crm.models import ProjectRelationship, Project
from timepiece.entries.models import Entry, Activity, Location

from timeclock.models import TaskList

def batch_import(file_name):
    project = Project.objects.first()
    activity = Activity.objects.first()
    location = Location.objects.first()
    group = Group.objects.first()

    with open(file_name, 'rb') as input_file:
        csv_reader = reader(input_file)
        for row in csv_reader:
            if csv_reader.line_num == 1:
                continue
            print row
            first_name = row.pop(0).replace('"', '')
            last_name = row.pop(0).replace('"', '')
            if last_name == '?':
                last_name = 'X'
            username = '{0}.{1}'.format(
                first_name.replace(' ', '').lower(), last_name.replace(' ', '').lower()
            )
            users = User.objects.filter(username=username)
            if not users.exists():
                password = 'gplvol{0}{1}'.format(first_name[0].lower(), last_name[0].lower())
                user = User.objects.create(
                    username=username, first_name=first_name, last_name=last_name
                )
                user.set_password(password)
                user.save()
                ProjectRelationship.objects.create(user=user, project=project)
                group.user_set.add(user)
            else:
                user = users.first()
            entry_day = row.pop(0).replace('"', '').split('-')
            for i in range(len(entry_day)):
                entry_day[i] = int(entry_day[i])
            in_time = row.pop(0).replace('"', '').replace(' ', ':').split(':')
            out_time = row.pop(0).replace('"', '').replace(' ', ':').split(':')
            in_time.pop()
            out_time.pop()
            for i in range(len(in_time)):
                in_time[i] = int(in_time[i])
                out_time[i] = int(out_time[i])
            if in_time[0] < 10:
                in_time[0] += 12
            if out_time[0] < 10:
                out_time[0] += 12
            tasks = row.pop(0).replace('"', '')
            entry = Entry.objects.create(
                user=user, project=project, location=location, activity=activity,
                start_time=datetime(*tuple(entry_day + in_time)),
                end_time=datetime(*tuple(entry_day + out_time))
            )
            TaskList.objects.create(entry=entry, tasks=tasks)
