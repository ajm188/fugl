import json

from ..base import FuglViewTestCase


class CreateCategoryTestCase(FuglViewTestCase):

    url = '/categories/'

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
        old_category_count = self.project.category_set.count()
        data = {
            'project': self.project.id,
            'title': 'my-category',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertEqual(data.get('title'), 'my-category')

        categories = self.project.category_set
        new_category_count = categories.count()
        self.assertEqual(old_category_count + 1, new_category_count)

        [c.delete() for c in categories.all()]

    def test_create_duplicate(self):
        self.create_category('my-category', project=self.project)
        old_count = self.project.category_set.count()

        data = {
            'project': self.project.id,
            'title': 'my-category',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertIn('non_field_errors', resp.data)

        categories = self.project.category_set
        self.assertEqual(old_count, categories.count())

        [c.delete() for c in categories.all()]

    def test_create_bad_data(self):
        data = {
            'project': self.project.id,
            'title': '',  # cannot be blank
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertNotIn('project', resp.data)

        data['title'] = 'blargh' * 10  # waaaay too long (> 50 chars)
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('title', resp.data)

    def test_create_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {
            'project': self.other_project.id,
            'title': 'my-title',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        self.other_project.category_set.all()[0].delete()
        access.delete()

    def test_create_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {
            'project': self.other_project.id,
            'title': 'my-title',
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


class RetrieveCategoryTestCase(FuglViewTestCase):

    _url = '/categories/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.category = self.create_category('test-category',
            project=self.project)
        self.url = self._url.format(pk=self.category.id)

        self.user = self.create_user('user')
        self.login(user=self.user, password='user')

    def tearDown(self):
        self.category.delete()
        self.project.delete()
        self.user.delete()

        super().tearDown()

    def test_retrieve_with_view_access_success(self):
        access = self.create_access(self.user, self.project)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertIn('title', data)
        self.assertEqual(data['title'], self.category.title)

        access.delete()

    def test_retrieve_with_no_access_fail(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)

    def test_retrieve_non_existent(self):
        url = self._url.format(pk=-1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


class UpdateCategoryTestCase(FuglViewTestCase):

    _url = '/categories/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.category = self.create_category('my-category',
            project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_update_success(self):
        url = self._url.format(pk=self.category.id)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data.get('title'), 'new-title')
        self.category.refresh_from_db()
        self.assertEqual(self.category.title, 'new-title')

        # undo the update
        self.category.title = 'my-category'
        self.category.save()

    def test_update_bad_data(self):
        url = self._url.format(pk=self.category.id)

        data = {'title': ''}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertEqual(self.category.title, 'my-category')

    def test_update_nonexistent(self):
        url = self._url.format(pk=-1)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_update_with_edit_access(self):
        category = self.create_category('a', project=self.other_project)
        url = self._url.format(pk=category.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {'title': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        category.refresh_from_db()
        self.assertEqual(category.title, 'blargh')
        category.delete()

        access.delete()

    def test_update_with_view_access(self):
        category = self.create_category('a', project=self.other_project)
        url = self._url.format(pk=category.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {'title': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        category.refresh_from_db()
        self.assertEqual(category.title, 'a')
        category.delete()

        access.delete()

    def test_update_with_no_access(self):
        category = self.create_category('a', project=self.other_project)
        url = self._url.format(pk=category.id)

        data = {'title': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        category.refresh_from_db()
        self.assertEqual(category.title, 'a')
        category.delete()


class DeleteCategoryTestCase(FuglViewTestCase):

    _url = '/categories/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.category = self.create_category('my-category',
            project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_delete_success(self):
        categories = self.project.category_set.count()
        url = self._url.format(pk=self.category.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.project.category_set.count(), categories - 1)

    def test_delete_nonexistent(self):
        url = self._url.format(pk=-1)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)

    def test_delete_with_edit_access(self):
        category = self.create_category('a', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        categories = self.other_project.category_set.count()
        url = self._url.format(pk=category.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.other_project.category_set.count(),
            categories - 1)

        access.delete()

    def test_delete_with_view_access(self):
        category = self.create_category('a', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        categories = self.other_project.category_set.count()
        url = self._url.format(pk=category.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.other_project.category_set.count(), categories)

        access.delete()
        category.delete()

    def test_delete_with_no_access(self):
        category = self.create_category('a', project=self.other_project)
        categories = self.other_project.category_set.count()
        url = self._url.format(pk=category.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.project.category_set.count(), categories)


class AvailableCategoryTestCase(FuglViewTestCase):

    url = '/categories/available/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.category = self.create_category('test-category',
            project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.category.delete()
        self.project.delete()
        self.other_user.delete()

        super().tearDown()

    def test_available_for_available(self):
        data = {
            'project': self.project.id,
            'title': 'some-other-category',
        }

        resp = self.client.get(self.url, data=data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertTrue(data['available'])

    def test_available_for_taken(self):
        data = {
            'project': self.project.id,
            'title': 'test-category',
        }

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertFalse(data['available'])

    def test_available_bad_data(self):
        data = {'project': self.project.id}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 400)

    def test_available_with_edit_access(self):
        data = {'project': self.other_project.id, 'title': 'blah'}

        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        access.delete()

    def test_available_with_view_access(self):
        data = {'project': self.other_project.id, 'title': 'blah'}

        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 404)

        access.delete()

    def test_available_with_no_access(self):
        data = {'project': self.other_project.id, 'title': 'blah'}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 404)

    def test_available_non_existent(self):
        data = {'project': -1, 'title': 'blah'}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 404)
