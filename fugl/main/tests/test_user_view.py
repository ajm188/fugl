"""
Test for main.views.user.UserHomeView.
"""

from django.test import Client
from .base import FuglTestCase


class UserHomeViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()

    def test_not_logged_in_redirect(self):
        response = self.client.get('/home/')
        # Assert that there will be a redirect.
        self.assertEqual(response.status_code, 302)
        # Assert that the redirect go to /login/
        self.assertIn('/login/', response.url)
        # Assert that the next page will be /home/:
        self.assertIn('next=/home/', response.url)

    def test_logged_in_home(self):
        self.assertTrue(self.client.login(username=self.admin_user.username,
                                          password=self.admin_password))
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
