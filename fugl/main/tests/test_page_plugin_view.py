"""
Tests for main.views.plugin class: CreatePluginView.

Tests:
CreatePluginViewTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form (404)
  - owner can access form
- POST:
  - not logged in user redirected to login
  - non-owner cannot post (404)
  - owner can create plugin

DeletePluginViewTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form (404)
  - owner can access form
    -> should return page confirming delete
- POST:
  - not logged in user redirected to login
  - non-owner cannot post (404)
  - owner can delete plugin
    - should be reflected in database
- Invalid:
  - No such user GET/POST 404
  - No such project GET/POST 404
  - No such plugin GET/POST 404

DeletePluginViewTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form (404)
  - owner can access form
    -> should return page confirming delete
- POST:
  - not logged in user redirected to login
  - non-owner cannot post (404)
  - owner can update plugin
    - should be reflected in database
- Invalid:
  - No such user GET/POST 404
  - No such project GET/POST 404
  - No such plugin GET/POST 404
"""

from django.test import Client
from .base import FuglTestCase
from main.models import User, Project, PagePlugin


class CreatePagePluginViewTestCase(FuglTestCase):

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

    def url_for(self, project):
        # return the "create plugin" url for a project
        return '/project/%s/%s/page_plugin/new' % (project.owner.username,
                                                   project.title)

    def login_other(self):
        # login the client as "otheruser"
        self.client.login(username=self.otheruser.username,
                          password=self.otherpass)

    def test_get_not_logged_in_redirect(self):
        url = self.url_for(self.project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_get_not_owner_404(self):
        url = self.url_for(self.project)
        self.login_other()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_owner(self):
        url = self.url_for(self.project)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_not_logged_in_redirect(self):
        url = self.url_for(self.project)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_post_not_owner_404(self):
        url = self.url_for(self.project)
        self.login_other()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_post_owner(self):
        url = self.url_for(self.project)
        data = {
            'title': 'Serious Business',
            'head_markup': '',
            'body_markup': 'whatever',
            'post_plugins': []
        }
        self.login()
        response = self.client.post(url, data)
        # should get redirected to the project home
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Page Plugin created!', response.content)
        plugs = PagePlugin.objects.filter(project=self.project,
                                          title=data['title'])
        self.assertEqual(len(plugs), 1)
        plugs[0].delete()

    def test_create_existing_plugin(self):
        data = {
            'title': 'Serious Business',
            'head_markup': '',
            'body_markup': 'whatever'
        }
        plug = PagePlugin.objects.create(title=data['title'],
                                         head_markup=data['head_markup'],
                                         body_markup=data['body_markup'],
                                         project=self.project)
        plug.save()
        url = self.url_for(self.project)
        self.login()

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        plugs = PagePlugin.objects.filter(project=self.project,
                                          title=data['title'])
        self.assertEqual(len(plugs), 1)
        plugs[0].delete()

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/page_plugin/new' % self.project.title
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        url = '/project/idontexist/%s/page_plugin/new' % self.project.title
        data = {
            'title': 'Serious Business',
            'head_markup': '',
            'body_markup': 'whatever'
        }
        self.login()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/doesntexist/page_plugin/new' % self.admin_user.username
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        url = '/project/%s/doesntexist/page_plugin/new' % self.admin_user.username
        data = {
            'title': 'Serious Business',
            'head_markup': '',
            'body_markup': 'whatever'
        }
        self.login()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)


class DeletePagePluginViewTestCase(FuglTestCase):
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

        self.plugin = PagePlugin.objects.create(title='default',
                                                head_markup='',
                                                body_markup='LOL',
                                                project=self.project)
        self.plugin.save()

    def tearDown(self):
        self.otheruser.delete()
        self.project.delete()
        self.plugin.delete()
        super().tearDownTheme()

    def url_for(self, project, plugin):
        # return the "delete plugin" url for a plugin
        return '/project/%s/%s/page_plugin/delete/%s' % (project.owner.username,
                                                         project.title,
                                                         plugin.id)

    def login_other(self):
        # login the client as "otheruser"
        self.client.login(username=self.otheruser.username,
                          password=self.otherpass)

    def test_get_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.plugin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_get_not_owner_404(self):
        url = self.url_for(self.project, self.plugin)
        self.login_other()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_owner(self):
        url = self.url_for(self.project, self.plugin)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf8')
        self.assertIn('delete', content)
        self.assertIn(self.project.title, content)
        self.assertIn(self.plugin.title, content)

    def test_post_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.plugin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_post_not_owner_404(self):
        url = self.url_for(self.project, self.plugin)
        self.login_other()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_post_owner(self):
        url = self.url_for(self.project, self.plugin)
        self.login()
        response = self.client.post(url)
        # should get redirected to the project home
        self.assertEqual(response.status_code, 302)
        redir_url = '/project/%s/%s' % (self.admin_user.username,
                                        self.project.title)
        redir_url = 'http://testserver' + redir_url
        self.assertIn(redir_url, response.url)

        # Assert that the change happened.
        with self.assertRaises(PagePlugin.DoesNotExist):
            self.plugin.refresh_from_db()

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/page_plugin/delete/%s' % (self.project.title,
                                                                self.plugin.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        url = '/project/idontexist/%s/page_plugin/delete/%s' % (self.project.title,
                                                                self.plugin.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/doesntexist/page_plugin/delete/%s' % (self.admin_user.username,
                                                                 self.plugin.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        url = '/project/%s/doesntexist/page_plugin/delete/%s' % (self.admin_user.username,
                                                                 self.plugin.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_plugin(self):
        url = '/project/%s/%s/page_plugin/delete/5464646' % (self.admin_user.username,
                                                             self.project.title)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_plugin(self):
        url = '/project/%s/%s/page_plugin/delete/5464646' % (self.admin_user.username,
                                                             self.project.title)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class UpdatePagePluginViewTestCase(FuglTestCase):
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

        self.plugin = PagePlugin.objects.create(title='default',
                                                head_markup='',
                                                body_markup='LOL',
                                                project=self.project)
        self.plugin.save()

    def tearDown(self):
        self.otheruser.delete()
        self.project.delete()
        self.plugin.delete()
        super().tearDownTheme()

    def url_for(self, project, plugin):
        # return the "delete plugin" url for a plugin
        return '/project/%s/%s/page_plugin/edit/%s' % (project.owner.username,
                                                       project.title,
                                                       plugin.id)

    def login_other(self):
        # login the client as "otheruser"
        self.client.login(username=self.otheruser.username,
                          password=self.otherpass)

    def test_get_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.plugin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_get_not_owner_404(self):
        url = self.url_for(self.project, self.plugin)
        self.login_other()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_owner(self):
        url = self.url_for(self.project, self.plugin)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf8')
        self.assertIn('Edit', content)
        self.assertIn('Page Plugin', content)
        self.assertIn(self.plugin.title, content)

    def test_post_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.plugin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_post_not_owner_404(self):
        url = self.url_for(self.project, self.plugin)
        self.login_other()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_post_owner(self):
        data = {
            'title': 'default_2',
            'head_markup': '',
            'body_markup': 'whatever',
        }
        url = self.url_for(self.project, self.plugin)
        self.login()
        response = self.client.post(url, data)
        # should get redirected to the project home
        self.assertEqual(response.status_code, 302)
        redir_url = '/project/%s/%s' % (self.admin_user.username,
                                        self.project.title)
        redir_url = 'http://testserver' + redir_url
        self.assertIn(redir_url, response.url)

        # Assert that the change happened.
        self.plugin.refresh_from_db()
        self.assertEqual(self.plugin.title, data['title'])

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/page_plugin/edit/%s' % (self.project.title,
                                                              self.plugin.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        url = '/project/idontexist/%s/page_plugin/edit/%s' % (self.project.title,
                                                              self.plugin.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/doesntexist/page_plugin/edit/%s' % (self.admin_user.username,
                                                               self.plugin.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        url = '/project/%s/doesntexist/page_plugin/edit/%s' % (self.admin_user.username,
                                                               self.plugin.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_category(self):
        url = '/project/%s/%s/page_plugin/edit/5464646' % (self.admin_user.username,
                                                           self.project.title)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_category(self):
        url = '/project/%s/%s/category/edit/5464646' % (self.admin_user.username,
                                                        self.project.title)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
