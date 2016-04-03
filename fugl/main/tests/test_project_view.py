"""
Tests for main.views.create_project class: CreateProjectView

Tests:
CreateProjectViewTestCase:
- GET:
  - not logged in user redirected to login
  - user can access form
- POST:
  - not logged in user redirected to login
  - user can create project
    - empty project name?
    - empty description?
    - invalid names?
CloneProjectViewTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form
  - user can access form
- POST:
  - not logged in user redirected to login
  - non-owner cannot clone
  - user can clone project
    - empty project name?
    - empty description?
    - invalid names?
DeleteProjectTestCase:
- GET:
  - not logged in user redirected to login
  - non-owner cannot access form (404)
  - user can access form
    -> form to confirm deletion
- POST:
  - not logged in user redirected to login
  - non-owner cannot post (404)
  - owner can create category
    - should be reflected in database
- Invalid:
  - No such user GET/POST 404
  - No such project GET/POST 404
"""

from django.test import Client
from .base import FuglTestCase
from main.models import Project, User


class CreateProjectViewTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()
        self.client = Client()

    def tearDown(self):
        super().tearDownTheme()

    url = '/project/create'

    def test_get_not_logged_in_redirect(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'http://testserver/login/?next=' + self.url)

    def test_get_logged_in(self):
        self.login()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Create Project', resp.content)

    def test_post_not_logged_in_redirect(self):
        data = {'title': 'blah', 'description': 'blah project'}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'http://testserver/login/?next=' + self.url)

    def test_post_logged_in(self):
        data = {'title': 'blah', 'description': 'blah project'}
        self.login()
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Project created!', resp.content)
        project_list = Project.objects.filter(owner=self.admin_user,
                                              title=data['title'])
        self.assertEqual(len(project_list), 1)
        project_list[0].delete()

    def test_empty_project_name(self):
        old_number_of_projects = len(Project.objects.all())
        data = {'title': '', 'description': 'blah project'}
        self.login()
        resp = self.client.post(self.url, data)
        # 200 doesn't mean failure, sadly
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'This field is required.', resp.content)
        new_number_of_projects = len(Project.objects.all())
        self.assertEqual(old_number_of_projects, new_number_of_projects)

    def test_duplicate_project_name(self):
        data = {'title': 'duplicate', 'description': 'dupe'}
        proj = Project.objects.create(title=data['title'],
                                      description=data['description'],
                                      owner=self.admin_user,
                                      theme=self.default_theme)
        proj.save()
        old_number_of_projects = len(Project.objects.all())
        self.login()
        resp = self.client.post(self.url, data)
        # 200 doesn't mean failure, sadly
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Project with that name already exists.', resp.content)
        new_number_of_projects = len(Project.objects.all())
        self.assertEqual(old_number_of_projects, new_number_of_projects)
        proj.delete()

    def test_forward_slash_in_project_name(self):
        old_number_of_projects = len(Project.objects.all())
        data = {'title': 'forward/slash', 'description': 'blah project'}
        self.login()
        resp = self.client.post(self.url, data)
        # 200 doesn't mean failure, sadly
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Not letters, digits, and -/_.', resp.content)
        new_number_of_projects = len(Project.objects.all())
        self.assertEqual(old_number_of_projects, new_number_of_projects)

    def test_post_too_long_title(self):
        old_number_of_projects = len(Project.objects.all())
        data = {
            'title': '123456789012345678901234567890123456789012345678901',
            'description': 'blah project',
        }
        self.login()
        resp = self.client.post(self.url, data)
        # 200 doesn't mean failure, sadly
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Ensure this value has at most 50 characters',
                      resp.content)
        new_number_of_projects = len(Project.objects.all())
        self.assertEqual(old_number_of_projects, new_number_of_projects)


class CloneProjectTestCase(FuglTestCase):

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
        self.project.delete()
        self.otheruser.delete()
        super().tearDownTheme()

    def url_for(self, project):
        # return the "delete project" url for a project
        return '/project/%s/%s/clone' % (project.owner.username,
                                         project.title)

    def login_other(self):
        # login the client as "otheruser"
        self.client.login(username=self.otheruser.username,
                          password=self.otherpass)

    def test_get_not_logged_in_redirect(self):
        url = self.url_for(self.project)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'http://testserver/login/?next=' + url)

    def test_get_not_owner_404(self):
        url = self.url_for(self.project)
        self.login_other()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_get_owner(self):
        url = self.url_for(self.project)
        self.login()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf8')
        self.assertIn('Clone ' + self.project.title, content)

    def test_post_not_logged_in_redirect(self):
        formdata = {'title': 'cloned'}
        url = self.url_for(self.project)
        resp = self.client.post(url, formdata)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'http://testserver/login/?next=' + url)

    def test_post_not_owner_404(self):
        formdata = {'title': 'cloned'}
        url = self.url_for(self.project)
        self.login_other()
        response = self.client.post(url, formdata)
        self.assertEqual(response.status_code, 404)

    def test_post_owner(self):
        formdata = {'title': 'cloned'}
        url = self.url_for(self.project)
        self.login()
        resp = self.client.post(url, formdata)
        # should get a 200,
        self.assertEqual(resp.status_code, 200)
        # Assert that the change happened.
        matching_projects = Project.objects.filter(owner=self.admin_user,
                                                   title='cloned')
        self.assertEqual(len(matching_projects), 1)
        # Clean it up.
        matching_projects[0].delete()

    def test_post_forward_slash(self):
        formdata = {'title': 'cloned/project'}
        url = self.url_for(self.project)
        self.login()
        resp = self.client.post(url, formdata)
        # should get a 200, with a form error
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf8')
        self.assertIn('Not letters, digits, and -/_.', content)
        # Assert that the change never happened
        matching_projects = Project.objects.filter(owner=self.admin_user)
        self.assertEqual(matching_projects.count(), 1)

    def test_post_empty_title(self):
        formdata = {'title': ''}
        url = self.url_for(self.project)
        self.login()
        resp = self.client.post(url, formdata)
        # should get a 200, with a form error
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf8')
        self.assertIn('field is required', content)
        # Assert that the change never happened
        matching_projects = Project.objects.filter(owner=self.admin_user)
        self.assertEqual(matching_projects.count(), 1)

    def test_post_too_long_title(self):
        formdata = {
            'title': '123456789012345678901234567890123456789012345678901'
        }
        url = self.url_for(self.project)
        self.login()
        resp = self.client.post(url, formdata)
        # should get a 200, with a form error
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf8')
        self.assertIn('Ensure this value has at most 50 characters', content)
        # Assert that the change never happened
        matching_projects = Project.objects.filter(owner=self.admin_user)
        self.assertEqual(matching_projects.count(), 1)

    def test_post_duplicate_title(self):
        formdata = {'title': self.project.title}
        url = self.url_for(self.project)
        self.login()
        resp = self.client.post(url, formdata)
        # should get a 200, with a form error
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf8')
        self.assertIn('Project with that name already exists', content)
        # Assert that the change never happened
        matching_projects = Project.objects.filter(owner=self.admin_user)
        self.assertEqual(matching_projects.count(), 1)

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/clone' % self.project.title
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        formdata = {'title': 'cloned'}
        url = '/project/idontexist/%s/clone' % self.project.title
        self.login()
        response = self.client.post(url, formdata)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/idontexist/clone' % self.admin_user.username
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        formdata = {'title': 'cloned'}
        url = '/project/%s/idontexist/clone' % self.admin_user.username
        self.login()
        response = self.client.post(url, formdata)
        self.assertEqual(response.status_code, 404)


class DeleteProjectTestCase(FuglTestCase):

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
        self.project.delete()
        self.otheruser.delete()
        super().tearDownTheme()

    def url_for(self, project):
        # return the "delete project" url for a project
        return '/project/%s/%s/delete' % (project.owner.username,
                                          project.title)

    def login_other(self):
        # login the client as "otheruser"
        self.client.login(username=self.otheruser.username,
                          password=self.otherpass)

    def test_get_not_logged_in_redirect(self):
        url = self.url_for(self.project)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'http://testserver/login/?next=' + url)

    def test_get_not_owner_404(self):
        url = self.url_for(self.project)
        self.login_other()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_get_owner(self):
        url = self.url_for(self.project)
        self.login()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf8')
        self.assertIn('delete', content)
        self.assertIn(self.project.title, content)

    def test_post_not_logged_in_redirect(self):
        url = self.url_for(self.project)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'http://testserver/login/?next=' + url)

    def test_post_not_owner_404(self):
        url = self.url_for(self.project)
        self.login_other()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_post_owner(self):
        url = self.url_for(self.project)
        self.login()
        resp = self.client.post(url)
        # should get redirected to home page
        self.assertEqual(resp.status_code, 302)
        redir_url = '/home'
        redir_url = 'http://testserver' + redir_url
        self.assertIn(redir_url, resp.url)

        # Assert that the change happened.
        with self.assertRaises(Project.DoesNotExist):
            self.project.refresh_from_db()

    def test_get_invalid_user(self):
        url = '/project/idontexist/%s/delete' % self.project.title
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_user(self):
        url = '/project/idontexist/%s/delete' % self.project.title
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_project(self):
        url = '/project/%s/idontexist/delete' % self.admin_user.username
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_project(self):
        url = '/project/%s/idontexist/delete' % self.admin_user.username
        self.login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
