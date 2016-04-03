"""
Test for main.views.project_home.ProjectDetailView.
"""

from django.test import Client
from .base import FuglTestCase
from main.models import Project, User


class ProjectDetailViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()
        self.otherpass = 'cock-of-the-rock'
        self.otheruser = User.objects.create_user('other_user',
                                                  'other@example.com',
                                                  self.otherpass)
        self.otheruser.save()
        self.project = Project.objects.create(
            title='testproj', description='test project', preview_url='',
            owner=self.admin_user, theme=self.default_theme
        )
        self.project.save()

    def tearDown(self):
        self.otheruser.delete()
        self.project.delete()
        super().tearDownTheme()

    def test_not_logged_in_redirect(self):
        response = self.client.get('/project/%s/%s' %
                                   (self.admin_user.username,
                                    self.project.title))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_not_logged_in_nonexisting_project_redirect(self):
        response = self.client.get('/project/%s/idontexist' %
                                   (self.admin_user.username,))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_not_logged_in_nonexisting_user_redirect(self):
        response = self.client.get('/project/idontexist/stilldontexist')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_logged_in(self):
        self.client.login(username=self.admin_user.username,
                          password=self.admin_password)
        response = self.client.get('/project/%s/%s' %
                                   (self.admin_user.username,
                                    self.project.title))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.project.title.encode('utf8'), response.content)

    def test_logged_in_nonexisting_project_404(self):
        self.client.login(username=self.admin_user.username,
                          password=self.admin_password)
        response = self.client.get('/project/%s/idontexist' %
                                   (self.admin_user.username,))
        self.assertEqual(response.status_code, 404)

    def test_logged_in_nonexisting_user_404(self):
        self.client.login(username=self.admin_user.username,
                          password=self.admin_password)
        response = self.client.get('/project/idontexist/stilldontexist')
        self.assertEqual(response.status_code, 404)

    def test_otheruser_404(self):
        self.assertTrue(self.client.login(username=self.otheruser.username,
                                          password=self.otherpass))
        response = self.client.get('/project/%s/%s' %
                                   (self.admin_user.username,
                                    self.project.title))
        self.assertEqual(response.status_code, 404)

    def test_otheruser_nonexisting_project_404(self):
        self.assertTrue(self.client.login(username=self.otheruser.username,
                                          password=self.otherpass))
        response = self.client.get('/project/%s/idontexist' %
                                   (self.admin_user.username,))
        self.assertEqual(response.status_code, 404)

    def test_otheruser_nonexisting_user_404(self):
        self.assertTrue(self.client.login(username=self.otheruser.username,
                                          password=self.otherpass))
        response = self.client.get('/project/idontexist/stilldontexist')
        self.assertEqual(response.status_code, 404)
