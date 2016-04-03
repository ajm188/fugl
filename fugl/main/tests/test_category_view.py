"""
Tests for main.views.category class: CreateCategoryView.

Tests:
CreateCategoryViewTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form (404)
  - owner can access form
- POST:
  - not logged in user redirected to login
  - non-owner cannot post (404)
  - owner can create category

DeleteCategoryViewTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form (404)
  - owner can access form
    -> should return page confirming delete
- POST:
  - not logged in user redirected to login
  - non-owner cannot post (404)
  - owner can delete category
    - should be reflected in database
- Invalid:
  - No such user GET/POST 404
  - No such project GET/POST 404
  - No such category GET/POST 404

DeleteCategoryViewTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form (404)
  - owner can access form
    -> should return page confirming delete
- POST:
  - not logged in user redirected to login
  - non-owner cannot post (404)
  - owner can update category
    - should be reflected in database
- Invalid:
  - No such user GET/POST 404
  - No such project GET/POST 404
  - No such category GET/POST 404
"""

from django.test import Client
from django.db import transaction
from .base import FuglTestCase
from main.models import User, Project, Category


class CreateCategoryViewTestCase(FuglTestCase):

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
        # return the "delete category" url for a project
        return '/project/%s/%s/category/new' % (project.owner.username,
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
        data = {'title': 'Serious Business'}
        self.login()
        response = self.client.post(url, data)
        # should get redirected to the project home
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Category created!', response.content)
        cats = Category.objects.filter(project=self.project,
                                       title=data['title'])
        self.assertEqual(len(cats), 1)
        cats[0].delete()

    def test_create_existing_category(self):
        data = {'title': 'Serious Business'}
        category = Category.objects.create(title=data['title'],
                                           project=self.project)
        category.save()
        url = self.url_for(self.project)
        self.login()

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes('<em>{0}</em> already exists'.format(data['title']), encoding='utf8'),
                      response.content)
        cats = Category.objects.filter(project=self.project,
                                       title=data['title'])
        self.assertEqual(len(cats), 1)
        cats[0].delete()

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/category/new' % self.project.title
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        url = '/project/idontexist/%s/category/new' % self.project.title
        data = {'title': 'Serious Business'}
        self.login()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/doesntexist/category/new' % self.admin_user.username
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        url = '/project/%s/doesntexist/category/new' % self.admin_user.username
        data = {'title': 'Serious Business'}
        self.login()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)


class DeleteCategoryViewTestCase(FuglTestCase):

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

        self.category = Category.objects.create(title='default',
                                                project=self.project)
        self.category.save()

    def tearDown(self):
        self.otheruser.delete()
        self.project.delete()
        self.category.delete()
        super().tearDownTheme()

    def url_for(self, project, category):
        # return the "delete category" url for a category
        return '/project/%s/%s/category/delete/%s' % (project.owner.username,
                                                project.title,
                                                category.id)

    def login_other(self):
        # login the client as "otheruser"
        self.client.login(username=self.otheruser.username,
                          password=self.otherpass)

    def test_get_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.category)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_get_not_owner_404(self):
        url = self.url_for(self.project, self.category)
        self.login_other()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_owner(self):
        url = self.url_for(self.project, self.category)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf8')
        self.assertIn('delete', content)
        self.assertIn(self.project.title, content)
        self.assertIn(self.category.title, content)

    def test_post_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.category)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_post_not_owner_404(self):
        url = self.url_for(self.project, self.category)
        self.login_other()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_post_owner(self):
        url = self.url_for(self.project, self.category)
        self.login()
        response = self.client.post(url)
        # should get redirected to the project home
        self.assertEqual(response.status_code, 302)
        redir_url = '/project/%s/%s' % (self.admin_user.username,
                                        self.project.title)
        redir_url = 'http://testserver' + redir_url
        self.assertIn(redir_url, response.url)

        # Assert that the change happened.
        with self.assertRaises(Category.DoesNotExist):
            self.category.refresh_from_db()

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/category/delete/%s' % (self.project.title,
                                                             self.category.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        url = '/project/idontexist/%s/category/delete/%s' % (self.project.title,
                                                             self.category.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/doesntexist/category/delete/%s' % (self.admin_user.username,
                                                              self.category.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        url = '/project/%s/doesntexist/category/delete/%s' % (self.admin_user.username,
                                                              self.category.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_category(self):
        url = '/project/%s/%s/category/delete/5464646' % (self.admin_user.username,
                                                     self.project.title)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_category(self):
        url = '/project/%s/%s/category/delete/5464646' % (self.admin_user.username,
                                                     self.project.title)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class UpdateCategoryViewTestCase(FuglTestCase):

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

        self.category = Category.objects.create(title='default',
                                                project=self.project)
        self.category.save()

    def tearDown(self):
        self.otheruser.delete()
        self.project.delete()
        self.category.delete()
        super().tearDownTheme()

    def url_for(self, project, category):
        # return the "delete category" url for a category
        return '/project/%s/%s/category/edit/%s' % (project.owner.username,
                                                project.title,
                                                category.id)

    def login_other(self):
        # login the client as "otheruser"
        self.client.login(username=self.otheruser.username,
                          password=self.otherpass)

    def test_get_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.category)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_get_not_owner_404(self):
        url = self.url_for(self.project, self.category)
        self.login_other()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_owner(self):
        url = self.url_for(self.project, self.category)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf8')
        self.assertIn('Update', content)
        self.assertIn('Category', content)
        self.assertIn(self.category.title, content)

    def test_post_not_logged_in_redirect(self):
        url = self.url_for(self.project, self.category)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/login/?next=' + url)

    def test_post_not_owner_404(self):
        url = self.url_for(self.project, self.category)
        self.login_other()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_post_owner(self):
        data = {
            'title': 'default_2'
        }
        url = self.url_for(self.project, self.category)
        self.login()
        response = self.client.post(url, data)
        # should get redirected to the project home
        self.assertEqual(response.status_code, 302)
        redir_url = '/project/%s/%s' % (self.admin_user.username,
                                        self.project.title)
        redir_url = 'http://testserver' + redir_url
        self.assertIn(redir_url, response.url)

        # Assert that the change happened.
        self.category.refresh_from_db()
        self.assertEqual(self.category.title, data['title'])

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/category/delete/%s' % (self.project.title,
                                                             self.category.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        url = '/project/idontexist/%s/category/delete/%s' % (self.project.title,
                                                             self.category.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/doesntexist/category/delete/%s' % (self.admin_user.username,
                                                              self.category.id)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        url = '/project/%s/doesntexist/category/delete/%s' % (self.admin_user.username,
                                                              self.category.id)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_category(self):
        url = '/project/%s/%s/category/delete/5464646' % (self.admin_user.username,
                                                     self.project.title)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_category(self):
        url = '/project/%s/%s/category/delete/5464646' % (self.admin_user.username,
                                                     self.project.title)
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
