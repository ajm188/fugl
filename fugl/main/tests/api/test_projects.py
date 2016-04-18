import json

from django.test import Client

from main.models import Project
from main.models import ProjectAccess
from main.models import User

from ..base import FuglViewTestCase


class ProjectViewSetTestCase(FuglViewTestCase):

    def setUp(self):
        super().setUp()

        self.user = self.admin_user
        self.owned_project = Project.objects.create(title='t', description='',
            theme=self.default_theme, owner=self.user)
        self.owned_project.save()

        self.other_user = User.objects.create(username='other',
            password='password')
        self.other_user.save()

        self.edit_project = Project.objects.create(title='edit',
            description='', theme=self.default_theme, owner=self.other_user)
        self.view_project = Project.objects.create(title='view',
            description='', theme=self.default_theme, owner=self.other_user)
        self.other_project = Project.objects.create(title='other',
            description='', theme=self.default_theme, owner=self.other_user)

        ProjectAccess.objects.create(user=self.user, project=self.edit_project,
            can_edit=True).save()
        ProjectAccess.objects.create(user=self.user, project=self.view_project,
            can_edit=False).save()

        self.login(user=self.user)

    def tearDown(self):
        super().tearDown()

        self.other_user.delete()
        self.owned_project.delete()

    _url = "/projects{0}"
    url = _url.format('/')
    owned_url = _url.format('/owned/')
    shared_url = _url.format('/shared/')
    detail_url = _url.format('/{}/')

    def test_owned_projects(self):
        resp = self.client.get(self.owned_url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 1)

        project = data[0]
        self.assertEqual(project['can_edit'], True)
        self.assertEqual(project['title'], self.owned_project.title)

    def test_shared_projects(self):
        resp = self.client.get(self.shared_url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 2)

        titles = [p.title for p in
                     [self.view_project, self.edit_project]]
        for project in data:
            self.assertIn(project['title'], titles)
            if project['title'] == self.view_project.title:
                self.assertEqual(project['can_edit'], False)
            else:
                self.assertEqual(project['can_edit'], True)

    def test_projects_index(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 3)

        titles = [p.title for p in
                    [self.owned_project, self.view_project, self.edit_project]]
        for project in data:
            self.assertIn(project['title'], titles)
            if project['title'] == self.view_project.title:
                self.assertEqual(project['can_edit'], False)
            else:
                self.assertEqual(project['can_edit'], True)
            if project['title'] == self.view_project.title:
                self.assertEqual(project['can_edit'], False)
            else:
                self.assertEqual(project['can_edit'], True)

    def test_project_detail_for_owned(self):
        resp = self.client.get(self.detail_url.format(self.owned_project.id))
        self.assertEqual(resp.status_code, 200)

    def test_project_detail_for_viewable(self):
        resp = self.client.get(self.detail_url.format(self.view_project.id))
        self.assertEqual(resp.status_code, 200)

    def test_project_detail_for_unviewable(self):
        resp = self.client.get(self.detail_url.format(self.other_project.id))
        self.assertEqual(resp.status_code, 404)

    def test_project_detail_for_nonexistent(self):
        resp = self.client.get(self.detail_url.format(-1))
        self.assertEqual(resp.status_code, 404)

    def test_project_update_for_owned(self):
        old_title = self.owned_project.title

        resp = self.client.put(self.detail_url.format(self.owned_project.id),
                data=json.dumps({'title': 'new-title'}),
                content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        self.owned_project.refresh_from_db()
        self.assertEqual(self.owned_project.title, 'new-title')
        self.assertNotEqual(self.owned_project.title, old_title)
        self.assertIn('title', resp.data)
        self.assertEqual(resp.data['title'], 'new-title')

    def test_project_update_bad_data(self):
        data = {'title': ''}
        resp = self.client.put(self.detail_url.format(self.owned_project.id),
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        self.owned_project.refresh_from_db()
        self.assertNotEqual(self.owned_project.title, '')
        self.assertIn('title', resp.data)
        title_error = resp.data['title']
        self.assertNotEqual(len(title_error), 0)

    def test_project_update_for_viewable(self):
        resp = self.client.put(self.detail_url.format(self.view_project.id))
        self.assertEqual(resp.status_code, 404)

    def test_project_update_for_editable(self):
        resp = self.client.put(self.detail_url.format(self.edit_project.id))
        self.assertEqual(resp.status_code, 200)

    def test_project_update_for_unviewable(self):
        resp = self.client.put(self.detail_url.format(self.other_project.id))
        self.assertEqual(resp.status_code, 404)

    def test_project_update_for_nonexistent(self):
        resp = self.client.put(self.detail_url.format(-1))
        self.assertEqual(resp.status_code, 404)

    def test_project_delete(self):
        project = Project.objects.create(title='ix-nay', description='',
            owner=self.user, theme=self.default_theme)
        num_projects = len(Project.objects.all())

        resp = self.client.delete(self.detail_url.format(project.id))
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(len(Project.objects.all()), num_projects - 1)

    def test_project_delete_unowned(self):
        num_projects = len(Project.objects.all())

        resp = self.client.delete(
            self.detail_url.format(self.edit_project.id)
        )
        self.assertEqual(resp.status_code, 404)

        self.assertEqual(len(Project.objects.all()), num_projects)

    def test_project_delete_nonexistent(self):
        num_projects = len(Project.objects.all())

        resp = self.client.delete(self.detail_url.format(-1))
        self.assertEqual(resp.status_code, 404)

        self.assertEqual(len(Project.objects.all()), num_projects)
