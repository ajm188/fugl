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
