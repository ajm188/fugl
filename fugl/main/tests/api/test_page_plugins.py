from ..base import FuglViewTestCase


class ListPagePluginTestCase(FuglViewTestCase):

    url = '/page_plugins/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.plug1 = self.create_page_plugin('plug1', project=self.project)
        self.plug2 = self.create_page_plugin('plug2', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)
        self.plug3 = self.create_page_plugin('plug3',
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
        self.assertEqual(len(data), self.project.pageplugin_set.count())
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


class CreatePagePluginTestCase(FuglViewTestCase):

    url = '/page_plugins/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.plug1 = self.create_page_plugin('plug1', project=self.project)

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
        count = self.project.pageplugin_set.count()
        data = {
            'project': self.project.id,
            'title': 'plug2',
            'head_markup': 'something',
            'body_markup': 'something else',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertEqual(data.get('title', None), 'plug2')
        self.assertEqual(self.project.pageplugin_set.count(), count + 1)
        new_plugs = self.project.pageplugin_set.filter(title='plug2')
        [p.delete() for p in new_plugs]

    def test_bad_data(self):
        count = self.project.pageplugin_set.count()
        data = {
            'project': self.project.id,
            'head_markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('title', resp.data)
        self.assertIn('body_markup', resp.data)
        self.assertNotIn('head_markup', resp.data)
        self.assertEqual(self.project.pageplugin_set.count(), count)

        data = {}
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

    def test_create_duplicate(self):
        count = self.project.pageplugin_set.count()
        data = {
            'project': self.project.id,
            'title': 'plug1',
            'head_markup': 'something',
            'body_markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(self.project.pageplugin_set.count(), count)

    def test_create_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)
        count = self.other_project.pageplugin_set.count()
        data = {
            'project': self.other_project.id,
            'title': 'plug2',
            'head_markup': 'something',
            'body_markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(
            self.other_project.pageplugin_set.count(),
            count + 1,
        )

        access.delete()
        self.other_project.pageplugin_set.all()[count].delete()

    def test_create_view_access(self):
        data = {
            'project': self.other_project.id,
            'title': 'plug2',
            'head_markup': 'something',
            'body_markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 404)

    def test_non_existent_project(self):
        data = {
            'project': -1,
            'title': 'plug2',
            'head_markup': 'something',
            'body_markup': 'something',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 404)


class RetrievePagePluginTestCase(FuglViewTestCase):

    _url = '/page_plugins/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.plug1 = self.create_page_plugin('plug1', project=self.project)
        self.plug2 = self.create_page_plugin('plug2', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)
        self.plug3 = self.create_page_plugin('plug3',
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
