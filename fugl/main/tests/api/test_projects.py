import json
from unittest import skip

from main.models import Project
from main.models import ProjectAccess
from main.models import User
from main.util import UserAccess

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
    access_url = detail_url + 'access/'

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

    def test_get_project_access_can_view(self):
        path = self.access_url.format(self.view_project.id)

        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(len(resp.data), 1)

    def test_get_project_access_cannot_view(self):
        path = self.access_url.format(self.other_project.id)

        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 404)

    def test_get_project_access_nonexistent(self):
        path = self.access_url.format(-1)

        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 404)

    def test_create_project_access_owner(self):
        path = self.access_url.format(self.owned_project.id)

        data = {'user': self.other_user.id, 'can_edit': True}
        resp = self.client.post(path, data=data)
        self.assertEqual(resp.status_code, 201)

        self.assertIn('can_edit', resp.data)
        self.assertTrue(resp.data['can_edit'])
        user = UserAccess(self.other_user)
        self.assertTrue(user.can_edit(self.owned_project))
        self.assertTrue(user.can_view(self.owned_project))

        ProjectAccess.objects.get(
            user=self.other_user,
            project=self.owned_project,
        ).delete()

    def test_create_project_access_not_owner(self):
        path = self.access_url.format(self.other_project.id)

        data = {'user': self.user.id, 'can_edit': True}
        resp = self.client.post(path, data=data)
        self.assertEqual(resp.status_code, 404)

    def test_create_project_access_bad_data(self):
        path = self.access_url.format(self.owned_project.id)

        data = {'can_edit': True}
        resp = self.client.post(path, data=data)
        self.assertEqual(resp.status_code, 400)

        data['user'] = self.other_user.id
        data['can_edit'] = 5
        resp = self.client.post(path, data=data)
        self.assertEqual(resp.status_code, 400)

    def test_create_project_access_duplicate(self):
        access = ProjectAccess.objects.create(
            user=self.other_user,
            project=self.owned_project,
            can_edit=True,
        )

        data = {'user': self.other_user.id}
        path = self.access_url.format(self.owned_project.id)
        resp = self.client.post(path, data=data)
        self.assertEqual(resp.status_code, 201)

        # make sure a dupe wasn't created
        self.assertEqual(
            len(ProjectAccess.objects.filter(user=self.other_user,
                                             project=self.owned_project)),
            1
        )
        access.delete()

    def test_update_project_access_owner(self):
        access = ProjectAccess.objects.create(
            user=self.other_user,
            project=self.owned_project,
            can_edit=True,
        )

        data = {'user': self.other_user.id, 'can_edit': False}
        path = self.access_url.format(self.owned_project.id)
        resp = self.client.put(path, data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        self.assertIn('can_edit', resp.data)
        self.assertEqual(resp.data['can_edit'], False)
        access.refresh_from_db()
        self.assertEqual(access.can_edit, False)

        access.delete()

    def test_update_project_access_not_owner(self):
        data = {'user': self.user.id, 'can_edit': True}
        path = self.access_url.format(self.other_project.id)
        resp = self.client.put(path, data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_update_project_access_nonexistent(self):
        data = {}
        path = self.access_url.format(-1)
        resp = self.client.put(path, data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        data['user'] = -1
        path = self.access_url.format(self.other_project.id)
        resp = self.client.put(path, data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_update_project_access_bad_data(self):
        path = self.access_url.format(self.owned_project.id)

        data = {'can_edit': True}
        resp = self.client.put(path, data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        data['user'] = self.other_user.id
        data['can_edit'] = 5
        resp = self.client.put(path, data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_delete_project_access_owner(self):
        access = ProjectAccess.objects.create(
            user=self.other_user,
            project=self.owned_project,
            can_edit=True,
        )

        data = {'user': self.other_user.id}

        path = self.detail_url.format(self.owned_project.id)
        resp = self.client.delete(path, data=data)
        self.assertEqual(resp.status_code, 204)

        self.assertFalse(
            ProjectAccess.objects.filter(user=self.other_user,
                project=self.owned_project).exists()
        )

    def test_delete_project_access_not_owner(self):
        data = {'user': self.user.id}

        path = self.detail_url.format(self.edit_project.id)
        resp = self.client.delete(path, data=data)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(ProjectAccess.objects.filter(
            user=self.user, project=self.edit_project).exists())

    def test_delete_project_access_nonexistent(self):
        data = {'user': self.other_user.id}

        path = self.detail_url.format(-1)
        resp = self.client.delete(path, data=data)
        self.assertEqual(resp.status_code, 404)


class CloneProjectTestCase(FuglViewTestCase):

    _url = '/projects/{pk}/clone/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('t', 'd',
            owner=self.admin_user)

        self.other_user = self.create_user(username='other')
        self.other_project = self.create_project('other-project', '',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.project.delete()
        self.other_project.delete()
        self.other_user.delete()

    def test_clone_success(self):
        url = self._url.format(pk=self.project.id)
        data = {'title': 'new-title'}

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'new-title')

        new_project_query = Project.objects.filter(owner=self.admin_user,
            title='new-title')
        self.assertTrue(new_project_query.exists())

        new_project = new_project_query.get()
        self.assertEqual(new_project.description, self.project.description)
        self.assertEqual(new_project.theme, self.default_theme)
        self.assertEqual(new_project.page_set.count(), 0)
        self.assertEqual(new_project.post_set.count(), 0)

        new_project.delete()

    def test_clone_all_attrs(self):
        page = self.create_page('page', content='content',
            project=self.project)
        post = self.create_post('post', content='content',
            project=self.project)
        theme = self.create_theme('my-theme', '/foo/bar', 'markup')
        self.project.theme = theme
        self.project.save()

        url = self._url.format(pk=self.project.id)
        data = {
            'title': 'new-title',
            'theme': True,
            'pages': True,
            'posts': True,
            'plugins': True,
        }

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'new-title')

        new_project_query = Project.objects.filter(owner=self.admin_user,
            title='new-title')
        self.assertTrue(new_project_query.exists())

        new_project = new_project_query.get()
        self.assertEqual(new_project.description, self.project.description)
        self.assertEqual(new_project.theme, self.project.theme)
        self.assertEqual(new_project.page_set.count(), 1)
        self.assertEqual(new_project.post_set.count(), 1)

        new_project.delete()

        self.project.theme = self.default_theme
        self.project.save()
        page.delete()
        post.delete()
        theme.delete()

    def test_clone_duplicate_title(self):
        count = self.admin_user.project_set.count()

        url = self._url.format(pk=self.project.id)
        data = {'title': self.project.title}

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertEqual(self.admin_user.project_set.count(), count)

    def test_clone_bad_data(self):
        count = self.admin_user.project_set.count()

        url = self._url.format(pk=self.project.id)
        data = {}

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertEqual(self.admin_user.project_set.count(), count)

    def test_clone_non_owner(self):
        count = self.admin_user.project_set.count()
        other_count = self.other_user.project_set.count()

        url = self._url.format(pk=self.other_project.id)
        data = {}

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 404)

        self.assertEqual(self.admin_user.project_set.count(), count)
        self.assertEqual(self.other_user.project_set.count(), other_count)

    def test_clone_wrong_method(self):
        count = self.admin_user.project_set.count()

        url = self._url.format(pk=self.project.id)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 405)

        self.assertEqual(self.admin_user.project_set.count(), count)

    def test_clone_non_existent(self):
        count = self.admin_user.project_set.count()

        url = self._url.format(pk=-1)
        data = {}

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 404)

        self.assertEqual(self.admin_user.project_set.count(), count)


class AvailableProjectTestCase(FuglViewTestCase):

    url = '/projects/available/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project1', '',
            owner=self.admin_user)
        self.other_user = self.create_user('other-user')
        self.other_project = self.create_project('other_project', '',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.project.delete()
        self.other_project.delete()
        self.other_user.delete()

        super().tearDown()

    def test_available_for_available(self):
        data = {'title': self.project.title + 'blah'}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        self.assertIn('available', resp.data)
        self.assertTrue(resp.data['available'])

    def test_available_for_taken(self):
        data = {'title': self.project.title}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        self.assertFalse(resp.data['available'])

    def test_available_bad_data(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 400)

    def test_available_wrong_method(self):
        resp = self.client.post(self.url, data={})
        self.assertEqual(resp.status_code, 405)

    def test_available_does_not_check_other_users_projects(self):
        data = {'title': self.other_project.title}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['available'])
