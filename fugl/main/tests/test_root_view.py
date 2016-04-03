"""
Test for main.views.root.root_controller.
"""

from django.test import Client
from .base import FuglTestCase


class RootViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()

    def test_not_logged_in_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_logged_in_go_to_home(self):
        self.assertTrue(self.client.login(username=self.admin_user.username,
                                          password=self.admin_password))
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home/', response.url)

    def test_other_response_types_500(self):
        self.assertTrue(self.client.login(username=self.admin_user.username,
                                          password=self.admin_password))
        response = self.client.post('/')
        self.assertEqual(response.status_code, 500)

        response = self.client.put('/')
        self.assertEqual(response.status_code, 500)

        response = self.client.head('/')
        self.assertEqual(response.status_code, 500)

        response = self.client.delete('/')
        self.assertEqual(response.status_code, 500)

        response = self.client.patch('/')
        self.assertEqual(response.status_code, 500)
