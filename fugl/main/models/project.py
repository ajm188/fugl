"""
Represents a project: a static website.
"""
from django.db import models
from django.core.exceptions import ValidationError

from re import compile

from .user import User
from .theme import Theme


def validate_project(value):
    reg = compile('[\w\-\ ]+\Z')
    if not reg.match(value):
        raise ValidationError('Not letters, digits, and -/_.', code='invalid')


class Project(models.Model):
    """
    Represents a project: a static website
    """
    class Meta:
        unique_together = (('title', 'owner'),)
        index_together = (('title', 'owner'),)

    title = models.CharField(max_length=50,
                             help_text='Required. Letters, digits, and -/_.',
                             validators=[validate_project])
    description = models.CharField(max_length=1000)
    preview_url = models.URLField()

    owner = models.ForeignKey(User)
    theme = models.ForeignKey('Theme')

    users = models.ManyToManyField(User, through='ProjectAccess',
        related_name='shared_projects')

    @property
    def project_home_url(self):
        return '/project/{0}/{1}'.format(self.owner.username, self.title)

    def get_pelican_conf(self, content_path='content'):
        """Returns pelicanconf correspnding to this Project."""
        project_plugins = self.projectplugin_set.all()
        project_plugins_str = [{'markup': p.markup} for p in project_plugins]
        template_args = {
            'author': self.owner.username,
            'site_name': self.title,
            'content_path': content_path,
            'theme': self.theme.filepath,
            'project_plugins_str': str(project_plugins_str),
        }
        return pelicanconf_template % template_args

    def clone(self, newtitle, theme, pages, posts, plugins):
        """
        Clone this project.

        Creates a new project with the same attributes and owner, but a
        different title.  Depending on the parameters given to this method, the
        theme, pages, posts, and/or plugins will also be copied to the new
        project.  Returns the cloned project, which has already been saved to
        the database.
        """
        kwargs = {
            'title': newtitle,
            'description': self.description,
            'owner': self.owner,
            'preview_url': '',
        }
        if theme:
            kwargs['theme'] = self.theme
        else:
            kwargs['theme'] = Theme.objects.get(title='default')

        new = Project.objects.create(**kwargs)
        new.save()

        # Copy over all the categories.
        for category in self.category_set.all():
            category.clone(new)

        # First, we clone all the plugins.  We keep a dictionary of page for
        # our pages and posts to lookup their new plugins when they are cloned.
        if plugins:
            plugin_dict = {}
            for plugin in self.pageplugin_set.all():
                plugin_dict[plugin] = plugin.clone(new)
            for plugin in self.projectplugin_set.all():
                plugin.clone(new)
        else:
            plugin_dict = None

        # Now, we clone pages and posts (if requested)
        if pages:
            for page in self.page_set.all():
                page.clone(new, plugin_dict)
        if posts:
            for post in self.post_set.all():
                post.clone(new, plugin_dict)

        return new


pelicanconf_template = """#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = '%(author)s'
SITENAME = '%(site_name)s'
SITEURL = ''
THEME = '%(theme)s'

PATH = '%(content_path)s'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = ()

# Social widget
SOCIAL = ()

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

PROJECT_PLUGINS = %(project_plugins_str)s

PLUGIN_PATHS = ['.']
PLUGINS = ['page_plugins']
"""
