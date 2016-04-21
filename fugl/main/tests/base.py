"""
Base class for Fugl tests that set up some database stuff.
"""

from django.test import Client
from django.test import TestCase
from django.utils import timezone

from main.models import Category
from main.models import Page
from main.models import Post
from main.models import Project
from main.models import ProjectAccess
from main.models import ProjectPlugin
from main.models import Tag
from main.models import Theme
from main.models import User


class FuglTestCase(TestCase):

    def setUpTheme(self):
        self.admin_password = 'cock-of-the-rock'
        self.admin_user = User.objects.create_user('admin_user',
                                                   'admin@example.com',
                                                   self.admin_password)
        self.admin_user.save()

        self.default_theme = Theme.objects.create(title='default',
                                                  filepath='notmyidea',
                                                  creator=self.admin_user)
        self.default_theme.save()

    def tearDownTheme(self):
        self.default_theme.save()
        self.admin_user.delete()

    def login(self, user=None, password=None):
        user = user if user is not None else self.admin_user
        password = password if password is not None else self.admin_password
        return self.client.login(username=user.username,
                                 password=password)

    def create_project(self, title, description='', **kwargs):
        kwargs['theme'] = kwargs.get('theme', self.default_theme)
        return self._create_object(
            Project, ('title', title), ('description', description),
            **kwargs
        )

    def create_user(self, username, **kwargs):
        kwargs.update({'username': username})
        kwargs['password'] = kwargs.get('password', username)
        user = User.objects.create_user(**kwargs)
        user.save()
        return user

    def _create_object(self, cls, *args, **kwargs):
        for name, val in args:
            kwargs[name] = val
        obj = cls.objects.create(**kwargs)
        obj.save()
        return obj

    def create_access(self, user, project, can_edit=False):
        return self._create_object(
            ProjectAccess,
            ('user', user), ('project', project), ('can_edit', can_edit),
        )

    def create_page(self, title, **kwargs):
        return self._create_object(Page, ('title', title), **kwargs)

    def create_post(self, title, content, **kwargs):
        timestamp = timezone.now()
        kwargs['date_created'] = kwargs.get('date_created', timestamp)
        kwargs['date_updated'] = kwargs.get('date_updated', timestamp)
        return self._create_object(
            Post,
            ('title', title), ('content', content),
            **kwargs
        )

    def create_category(self, title, **kwargs):
        return self._create_object(Category, ('title', title), **kwargs)

    def create_tag(self, title, **kwargs):
        return self._create_object(Tag, ('title', title), **kwargs)

    def create_theme(self, title, filepath, markup, **kwargs):
        kwargs['creator'] = kwargs.get('creator', self.admin_user)
        return self._create_object(
            Theme,
            ('title', title), ('filepath', filepath), ('body_markup', markup),
            **kwargs
        )

    def create_project_plugin(self, title, **kwargs):
        kwargs['markup'] = kwargs.get('markup', 'markup')
        return self._create_object(ProjectPlugin, ('title', title), **kwargs)


class FuglViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()
