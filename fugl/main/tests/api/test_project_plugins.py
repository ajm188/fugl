import json

from ..base import FuglViewTestCase


class ListProjectPluginTestCase(FuglViewTestCase):

    url = '/project_plugins/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.plug1 = self.create_project_plugin('plug1', project=self.project)
        self.plug2 = self.create_project_plugin('plug2', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)
        self.plug3 = self.create_project_plugin('plug3',
            project=self.other_project)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.other_project.delete()
        self.other_user.delete()
        self.plug1.delete()
        self.plug2.delete()
        self.plug3.delete()
        self.project.delete()

        super().tearDown()

    def test_list(self):
        data = {'project': self.project.id}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), self.project.projectplugin_set.count())
        plug1 = data[0]
        self.assertEqual(plug1.get('title', None), self.plug1.title)

    def test_list_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {'project': self.other_project.id}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('title', None), self.plug3.title)

        access.delete()

    def test_list_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {'project': self.other_project.id}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('title', None), self.plug3.title)

        access.delete()

    def test_list_with_no_access(self):
        data = {'project': self.other_project.id}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 404)

    def test_list_non_existent_project(self):
        data = {'project': -1}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 404)

    def test_list_bad_data(self):
        resp = self.client.get(self.url, {})
        self.assertEqual(resp.status_code, 400)


class CreateProjectPluginTestCase(FuglViewTestCase):

    url = '/project_plugins/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.plug1 = self.create_project_plugin('plug1', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.other_project.delete()
        self.other_user.delete()
        self.plug1.delete()
        self.project.delete()

        super().tearDown()

    def test_create_success(self):
        count = self.project.projectplugin_set.count()
        data = {
            'project': self.project.id,
            'title': 'plug2',
            'markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertEqual(data.get('title', None), 'plug2')
        self.assertEqual(self.project.projectplugin_set.count(), count + 1)
        new_plugs = self.project.projectplugin_set.filter(title='plug2')
        [p.delete() for p in new_plugs]

    def test_bad_data(self):
        count = self.project.projectplugin_set.count()
        data = {
            'project': self.project.id,
            'markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('title', resp.data)
        self.assertNotIn('markup', resp.data)
        self.assertEqual(self.project.projectplugin_set.count(), count)

        data = {}
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

    def test_create_duplicate(self):
        count = self.project.projectplugin_set.count()
        data = {
            'project': self.project.id,
            'title': 'plug1',
            'markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(self.project.projectplugin_set.count(), count)

    def test_create_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)
        count = self.other_project.projectplugin_set.count()
        data = {
            'project': self.other_project.id,
            'title': 'plug2',
            'markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(
            self.other_project.projectplugin_set.count(),
            count + 1,
        )

        access.delete()
        self.other_project.projectplugin_set.all()[count].delete()

    def test_create_view_access(self):
        data = {
            'project': self.other_project.id,
            'title': 'plug2',
            'markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 404)

    def test_non_existent_project(self):
        data = {
            'project': -1,
            'title': 'plug2',
            'markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 404)


class RetrieveProjectPluginTestCase(FuglViewTestCase):

    _url = '/project_plugins/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.plug1 = self.create_project_plugin('plug1', project=self.project)
        self.plug2 = self.create_project_plugin('plug2', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)
        self.plug3 = self.create_project_plugin('plug3',
            project=self.other_project)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.other_project.delete()
        self.other_user.delete()
        self.plug1.delete()
        self.plug2.delete()
        self.plug3.delete()
        self.project.delete()

        super().tearDown()

    def test_retrieve(self):
        plug = self.plug1
        url = self._url.format(pk=plug.id)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(resp.data['title'], plug.title)
        self.assertNotEqual(resp.data['title'], self.plug2.title)

    def test_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        plug = self.plug3
        url = self._url.format(pk=plug.id)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data['title'], plug.title)

        access.delete()

    def test_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        plug = self.plug3
        url = self._url.format(pk=plug.id)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data['title'], plug.title)

        access.delete()

    def test_with_no_access(self):
        plug = self.plug3
        url = self._url.format(pk=plug.id)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_non_existent(self):
        url = self._url.format(pk=-1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


class UpdateProjectPluginTestCase(FuglViewTestCase):

    _url = '/project_plugins/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.plug1 = self.create_project_plugin('plug1', project=self.project)
        self.plug2 = self.create_project_plugin('plug2', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)
        self.plug3 = self.create_project_plugin('plug3',
            project=self.other_project)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.other_project.delete()
        self.other_user.delete()
        self.plug1.delete()
        self.plug2.delete()
        self.plug3.delete()
        self.project.delete()

        super().tearDown()

    def test_update(self):
        plug = self.plug1
        url = self._url.format(pk=plug.id)

        old_title = plug.title
        data = {'title': 'new-title'}

        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(resp.data['title'], 'new-title')

        plug.refresh_from_db()
        self.assertEqual(plug.title, data['title'])
        plug.title = old_title
        plug.save()

    def test_update_bad_data(self):
        plug = self.plug1
        url = self._url.format(pk=plug.id)

        data = {'title': ''}

        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        data = resp.data
        self.assertIn('title', data)
        plug.refresh_from_db()
        self.assertNotEqual(plug.title, '')

    def test_update_duplicate_title(self):
        plug = self.plug1
        url = self._url.format(pk=plug.id)

        old_title = plug.title
        data = {'title': 'plug2'}

        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        data = resp.data
        self.assertIn('non_field_errors', data)
        plug.refresh_from_db()
        self.assertNotEqual(plug.title, 'plug2')

    def test_update_change_project(self):
        plug = self.plug1
        url = self._url.format(pk=plug.id)

        old_title = plug.title
        data = {'project': self.other_project.id}

        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        plug.refresh_from_db()
        self.assertNotEqual(plug.project, self.other_project)

    def test_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        plug = self.plug3
        old_title = plug.title
        url = self._url.format(pk=plug.id)
        data = {'title': 'new-title'}

        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data['title'], 'new-title')
        plug.refresh_from_db()
        self.assertEqual(plug.title, data['title'])

        plug.title = old_title
        plug.save()

        access.delete()

    def test_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        plug = self.plug3
        url = self._url.format(pk=plug.id)
        data = {'title': 'new-title'}

        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        plug.refresh_from_db()
        self.assertNotEqual(plug.title, 'new-title')

        access.delete()

    def test_with_no_access(self):
        plug = self.plug3
        old_title = plug.title
        url = self._url.format(pk=plug.id)
        data = {'title': 'new-title'}

        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        plug.refresh_from_db()
        self.assertNotEqual(plug.title, 'new-title')

    def test_non_existent(self):
        url = self._url.format(pk=-1)
        resp = self.client.put(url, data=json.dumps({}),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)


class DeleteProjectPluginTestCase(FuglViewTestCase):

    _url = '/project_plugins/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.other_project.delete()
        self.other_user.delete()
        self.project.delete()

        super().tearDown()

    def test_delete(self):
        plug = self.create_project_plugin('plug', project=self.project)
        count = self.project.projectplugin_set.count()
        url = self._url.format(pk=plug.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.project.projectplugin_set.count(), count - 1)

    def test_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        plug = self.create_project_plugin('plug', project=self.other_project)
        count = self.other_project.projectplugin_set.count()
        url = self._url.format(pk=plug.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(
            self.other_project.projectplugin_set.count(),
            count - 1,
        )

        access.delete()

    def test_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        plug = self.create_project_plugin('plug', project=self.other_project)
        count = self.other_project.projectplugin_set.count()
        url = self._url.format(pk=plug.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.other_project.projectplugin_set.count(), count)

        access.delete()
        plug.delete()

    def test_with_no_access(self):
        plug = self.create_project_plugin('plug', project=self.other_project)
        count = self.other_project.projectplugin_set.count()
        url = self._url.format(pk=plug.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.other_project.projectplugin_set.count(), count)

        plug.delete()

    def test_non_existent(self):
        url = self._url.format(pk=-1)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
