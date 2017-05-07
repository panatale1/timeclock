from timepiece.entries.models import Entry

from django.db import models


class TaskList(models.Model):
    entry = models.OneToOneField(Entry, related_name='tasks')
    tasks = models.CharField(max_length=255, null=True, blank=True)
