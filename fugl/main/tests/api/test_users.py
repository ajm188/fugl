"""
Tests for main.api.users.UserViewSet.
"""

from django.test import Client

from main.models import User

from ..base import FuglTestCase


class UserViewSetTestCase(FuglTestCase):

    user_path = '/users/'
    available_path = user_path + 'available/'

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()

    def test_create_user(self):
        post_data = {'username': 'test_user', 'password': 'test_pass',
                     'email': 'example@example.com'}
        response = self.client.post(self.user_path, post_data)
        self.assertEqual(response.status_code, 201)
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 1)
        # Finally, we can delete the user we created.
        users[0].delete()

    def test_duplicate_username(self):
        user = User.objects.create(username='test_user', password='test_pass',)
        user.save()

        post_data = {'username': 'test_user', 'password': 'test_pass',
                     'email': 'example@example.com'}
        response = self.client.post(self.user_path, post_data)
        self.assertEqual(response.status_code, 400)
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 1)
        # Finally, we can delete the user we created.
        user.delete()

    def test_post_invalid_email_fails(self):
        post_data = {'username': 'test_user', 'password': 'test_pass',
                     'email': 'I am not really an email address!'}
        response = self.client.post(self.user_path, post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Enter a valid email address', response.content)
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)

    def test_post_invalid_username_with_spaces_fails(self):
        post_data = {'username': 'test user', 'password': 'test_pass',
                     'email': 'example@example.com'}
        response = self.client.post(self.user_path, post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Enter a valid username', response.content)
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)

    def test_post_invalid_username_invalid_character_fails(self):
        post_data = {'username': 'test/user', 'password': 'test_pass',
                     'email': 'example@example.com'}
        response = self.client.post(self.user_path, post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Enter a valid username', response.content)
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)

    def test_post_invalid_username_too_long_fails(self):
        post_data = {'username': '0123456789012345678901234567890',
                     'password': 'test_pass', 'email': 'example@example.com'}
        response = self.client.post(self.user_path, post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Ensure this field has no more than', response.content)
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)

    def test_username_check_success(self):
        data = {'username': 'test_user'}
        resp = self.client.get(self.available_path, data)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'true', resp.content)

    def test_username_check_taken(self):
        user = User.objects.create(username='test_user', password='test_pass',)
        user.save()

        data = {'username': 'test_user'}
        resp = self.client.get(self.available_path, data)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'false', resp.content)

        user.delete()
