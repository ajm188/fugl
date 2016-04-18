# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20160414_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectaccess',
            name='project',
            field=models.ForeignKey(to='main.Project'),
        ),
        migrations.AlterField(
            model_name='projectaccess',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='projectaccess',
            unique_together=set([]),
        ),
        migrations.AlterIndexTogether(
            name='projectaccess',
            index_together=set([]),
        ),
    ]
