"""
Tests for main.views.registration.RegistrationView.
"""

from django.test import Client
from .base import FuglTestCase
from main.models import User


class RegistrationViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()

    def test_get_not_logged_in_returns_form(self):
        response = self.client.get('/register/')
        # We should get a 200, and it should contain the form.
        self.assertEqual(response.status_code, 200)

    def test_post_creates_user(self):
        post_data = {'username': 'test_user', 'password': 'test_pass',
                     'email': 'example@example.com'}
        response = self.client.post('/register/', post_data)
        # We should get a 200 OK:
        self.assertEqual(response.status_code, 200)
        # That contains "Registration successful"
        self.assertIn(b'Registration successful', response.content)
        # After this, we should have a test_user in the database.
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 1)
        # Finally, we can delete the user we created.
        users[0].delete()

    def test_duplicate_username(self):
        post_data = {'username': self.admin_user.username,
                     'password': 'test_pass', 'email': 'example@example.com'}
        response = self.client.post('/register/', post_data)
        # We should get a 200 OK:
        self.assertEqual(response.status_code, 200)
        # That contains "Registration successful"
        self.assertIn(b'A user with that username already exists.',
                      response.content)
        # After this, we should still have an admin_user, but NOT a test_user
        # in the database.
        admin_users = User.objects.filter(username=self.admin_user.username)
        self.assertEqual(len(admin_users), 1)
        test_users = User.objects.filter(username='test_user')
        self.assertEqual(len(test_users), 0)

    def test_post_invalid_email_fails(self):
        post_data = {'username': 'test_user', 'password': 'test_pass',
                     'email': 'I am not really an email address!'}
        response = self.client.post('/register/', post_data)
        # We should get a 200 OK (even though the registration fails)
        self.assertEqual(response.status_code, 200)
        # It should contain a message about an invalid email address.
        self.assertIn(b'Enter a valid email address', response.content)
        # After this, we should NOT have a test_user in the database.
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)

    def test_post_invalid_username_with_spaces_fails(self):
        post_data = {'username': 'test user', 'password': 'test_pass',
                     'email': 'example@example.com'}
        response = self.client.post('/register/', post_data)
        # We should get a 200 OK (even though the registration fails)
        self.assertEqual(response.status_code, 200)
        # It should contain a message about an invalid email address.
        self.assertIn(b'Enter a valid username', response.content)
        # After this, we should NOT have a test_user in the database.
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)

    def test_post_invalid_username_invalid_character_fails(self):
        post_data = {'username': 'test/user', 'password': 'test_pass',
                     'email': 'example@example.com'}
        response = self.client.post('/register/', post_data)
        # We should get a 200 OK (even though the registration fails)
        self.assertEqual(response.status_code, 200)
        # It should contain a message about an invalid email address.
        self.assertIn(b'Enter a valid username', response.content)
        # After this, we should NOT have a test_user in the database.
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)

    def test_post_invalid_username_too_long_fails(self):
        post_data = {'username': '0123456789012345678901234567890',
                     'password': 'test_pass', 'email': 'example@example.com'}
        response = self.client.post('/register/', post_data)
        # We should get a 200 OK (even though the registration fails)
        self.assertEqual(response.status_code, 200)
        # It should contain a message about an invalid email address.
        self.assertIn(b'Ensure this value has at most', response.content)
        # After this, we should NOT have a test_user in the database.
        users = User.objects.filter(username='test_user')
        self.assertEqual(len(users), 0)
