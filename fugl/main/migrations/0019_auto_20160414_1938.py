# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0018_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('can_edit', models.BooleanField(default=False)),
                ('project', models.OneToOneField(to='main.Project')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(related_name='shared_projects', through='main.ProjectAccess', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='projectaccess',
            unique_together=set([('user', 'project')]),
        ),
        migrations.AlterIndexTogether(
            name='projectaccess',
            index_together=set([('user', 'project')]),
        ),
    ]
