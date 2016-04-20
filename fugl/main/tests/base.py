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
        kwargs.update({'title': title, 'description': description})
        kwargs['theme'] = kwargs.get('theme', self.default_theme)
        project = Project.objects.create(**kwargs)
        project.save()
        return project

    def create_user(self, username, **kwargs):
        kwargs.update({'username': username})
        kwargs['password'] = kwargs.get('password', username)
        user = User.objects.create_user(**kwargs)
        user.save()
        return user

    def create_access(self, user, project, can_edit=False):
        access = ProjectAccess.objects.create(
            user=user, project=project, can_edit=can_edit)
        access.save()
        return access

    def create_page(self, title, **kwargs):
        kwargs.update({'title': title})
        page = Page.objects.create(**kwargs)
        page.save()
        return page

    def create_post(self, title, content, **kwargs):
        kwargs.update({'title': title, 'content': content})
        timestamp = timezone.now()
        kwargs['date_created'] = kwargs.get('date_created', timestamp)
        kwargs['date_updated'] = kwargs.get('date_updated', timestamp)
        post = Post.objects.create(**kwargs)
        post.save()
        return post

    def create_category(self, title, **kwargs):
        kwargs.update({'title': title})
        category = Category.objects.create(**kwargs)
        category.save()
        return category

    def create_tag(self, title, **kwargs):
        kwargs.update({'title': title})
        tag = Tag.objects.create(**kwargs)
        tag.save()
        return tag


class FuglViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()
