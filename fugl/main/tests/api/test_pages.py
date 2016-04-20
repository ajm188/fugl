import json

from ..base import FuglViewTestCase


class CreatePageTestCase(FuglViewTestCase):

    url = '/pages/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.project.delete()
        self.other_project.delete()
        self.other_user.delete()

        super().tearDown()

    def test_create_success(self):
        old_pages = [p for p in self.project.page_set.all()]
        data = {
            'project': self.project.id,
            'title': 'my-page',
            'content': 'page content',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertEqual(data.get('title'), 'my-page')
        self.assertEqual(data.get('content'), 'page content')

        new_pages = self.project.page_set.all()
        self.assertNotEqual(len(old_pages), len(new_pages))

        new_pages[0].delete()

    def test_create_bad_data(self):
        data = {
            'project': self.project.id,
            'title': '',  # cannot be blank
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertIn('content', resp.data)
        self.assertNotIn('project', resp.data)

        del data['project']
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

    def test_create_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {
            'project': self.other_project.id,
            'title': 'my-title',
            'content': 'blah',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        self.other_project.page_set.all()[0].delete()
        access.delete()

    def test_create_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {
            'project': self.other_project.id,
            'title': 'my-title',
            'content': 'blah',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 404)

    def test_create_with_no_access(self):
        data = {'project': self.other_project.id}
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 404)

    def test_create_with_nonexistent_project(self):
        data = {
            'project': -1,
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 404)


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

    _url = '/pages/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.page = self.create_page('my-page', content='blah',
            project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_update_success(self):
        url = self._url.format(pk=self.page.id)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data.get('title'), 'new-title')
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, 'new-title')

        # undo the update
        self.page.title = 'my-page'
        self.page.save()

    def test_update_bad_data(self):
        url = self._url.format(pk=self.page.id)

        data = {'title': ''}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertEqual(self.page.title, 'my-page')

    def test_update_nonexistent(self):
        url = self._url.format(pk=-1)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_update_with_edit_access(self):
        page = self.create_page('a', content='b', project=self.other_project)
        url = self._url.format(pk=page.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {'content': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        page.refresh_from_db()
        self.assertEqual(page.content, 'blargh')
        page.delete()

        access.delete()

    def test_update_with_view_access(self):
        page = self.create_page('a', content='b', project=self.other_project)
        url = self._url.format(pk=page.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {'content': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        page.refresh_from_db()
        self.assertEqual(page.content, 'b')
        page.delete()

        access.delete()

    def test_update_with_no_access(self):
        page = self.create_page('a', content='b', project=self.other_project)
        url = self._url.format(pk=page.id)

        data = {'content': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        page.refresh_from_db()
        self.assertEqual(page.content, 'b')
        page.delete()


class DeletePageTestCase(FuglViewTestCase):

    _url = '/pages/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.page = self.create_page('my-page', content='blah',
            project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_delete_success(self):
        pages = self.project.page_set.count()
        url = self._url.format(pk=self.page.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.project.page_set.count(), pages - 1)

    def test_delete_nonexistent(self):
        url = self._url.format(pk=-1)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)

    def test_delete_with_edit_access(self):
        page = self.create_page('a', content='b', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        pages = self.other_project.page_set.count()
        url = self._url.format(pk=page.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.other_project.page_set.count(), pages - 1)

        access.delete()

    def test_delete_with_view_access(self):
        page = self.create_page('a', content='b', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        pages = self.other_project.page_set.count()
        url = self._url.format(pk=page.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.other_project.page_set.count(), pages)

        access.delete()
        page.delete()

    def test_delete_with_no_access(self):
        page = self.create_page('a', content='b', project=self.other_project)
        pages = self.other_project.page_set.count()
        url = self._url.format(pk=page.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.project.page_set.count(), pages)
