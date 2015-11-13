# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20151112_2040'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectplugin',
            unique_together=set([('title', 'project')]),
        ),
        migrations.AlterIndexTogether(
            name='projectplugin',
            index_together=set([('title', 'project')]),
        ),
    ]
