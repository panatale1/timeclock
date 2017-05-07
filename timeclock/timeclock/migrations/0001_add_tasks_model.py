# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0003_auto_20151217_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.CharField(max_length=255, null=True, blank=True)),
                ('entry', models.OneToOneField(related_name='tasks', to='entries.Entry')),
            ],
        ),
    ]
