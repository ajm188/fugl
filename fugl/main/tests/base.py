"""
Base class for Fugl tests that set up some database stuff.
"""

from django.test import Client
from django.test import TestCase

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
        user = user or self.admin_user
        password = password or self.admin_password
        return self.client.login(username=user.username,
                                 password=password)


class FuglViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()
