from ..base import FuglViewTestCase


class CreatePageTestCase(FuglViewTestCase):

    pass


class RetrievePageTestCase(FuglViewTestCase):

    _url = '/pages/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.page = self.create_page('test-page', project=self.project)
        self.url = self._url.format(pk=self.page.id)

        self.user = self.create_user('user')
        self.login(user=self.user, password='user')

    def tearDown(self):
        self.page.delete()
        self.project.delete()
        self.user.delete()

        super().tearDown()

    def test_retrieve_with_view_access_success(self):
        access = self.create_access(self.user, self.project)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertIn('title', data)
        self.assertEqual(data['title'], self.page.title)

        access.delete()

    def test_retrieve_with_no_access_fail(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)

    def test_retrieve_non_existent(self):
        url = self._url.format(pk=-1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


class UpdatePageTestCase(FuglViewTestCase):

    pass


class DeletePageTestCase(FuglViewTestCase):

    pass
