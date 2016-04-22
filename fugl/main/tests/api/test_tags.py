import json

from ..base import FuglViewTestCase


class ListTagTestCase(FuglViewTestCase):

    url = '/tags/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.tag1 = self.create_tag('tag1', project=self.project)
        self.tag2 = self.create_tag('tag2', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)
        self.tag3 = self.create_tag('tag3', project=self.other_project)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.other_project.delete()
        self.other_user.delete()
        self.tag1.delete()
        self.tag2.delete()
        self.tag3.delete()
        self.project.delete()

        super().tearDown()

    def test_list(self):
        data = {'project': self.project.id}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), self.project.tag_set.count())
        tag1 = data[0]
        self.assertEqual(tag1.get('title', None), self.tag1.title)

    def test_list_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {'project': self.other_project.id}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('title', None), self.tag3.title)

        access.delete()

    def test_list_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {'project': self.other_project.id}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('title', None), self.tag3.title)

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


class CreateTagTestCase(FuglViewTestCase):

    url = '/tags/'

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
        old_tag_count = self.project.tag_set.count()
        data = {
            'project': self.project.id,
            'title': 'my-tag',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertEqual(data.get('title'), 'my-tag')

        tags = self.project.tag_set
        new_tag_count = tags.count()
        self.assertEqual(old_tag_count + 1, new_tag_count)

        [c.delete() for c in tags.all()]

    def test_create_duplicate(self):
        self.create_tag('my-tag', project=self.project)
        old_count = self.project.tag_set.count()

        data = {
            'project': self.project.id,
            'title': 'my-tag',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertIn('non_field_errors', resp.data)

        tags = self.project.tag_set
        self.assertEqual(old_count, tags.count())

        [c.delete() for c in tags.all()]

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

        self.other_project.tag_set.all()[0].delete()
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


class RetrieveTagTestCase(FuglViewTestCase):

    _url = '/tags/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.tag = self.create_tag('test-tag', project=self.project)
        self.url = self._url.format(pk=self.tag.id)

        self.user = self.create_user('user')
        self.login(user=self.user, password='user')

    def tearDown(self):
        self.tag.delete()
        self.project.delete()
        self.user.delete()

        super().tearDown()

    def test_retrieve_with_view_access_success(self):
        access = self.create_access(self.user, self.project)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertIn('title', data)
        self.assertEqual(data['title'], self.tag.title)

        access.delete()

    def test_retrieve_with_no_access_fail(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)

    def test_retrieve_non_existent(self):
        url = self._url.format(pk=-1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


class UpdateTagTestCase(FuglViewTestCase):

    _url = '/tags/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.tag = self.create_tag('my-tag', project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_update_success(self):
        url = self._url.format(pk=self.tag.id)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data.get('title'), 'new-title')
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.title, 'new-title')

        # undo the update
        self.tag.title = 'my-tag'
        self.tag.save()

    def test_update_bad_data(self):
        url = self._url.format(pk=self.tag.id)

        data = {'title': ''}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertEqual(self.tag.title, 'my-tag')

    def test_update_nonexistent(self):
        url = self._url.format(pk=-1)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_update_with_edit_access(self):
        tag = self.create_tag('a', project=self.other_project)
        url = self._url.format(pk=tag.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {'title': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        tag.refresh_from_db()
        self.assertEqual(tag.title, 'blargh')
        tag.delete()

        access.delete()

    def test_update_with_view_access(self):
        tag = self.create_tag('a', project=self.other_project)
        url = self._url.format(pk=tag.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {'title': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        tag.refresh_from_db()
        self.assertEqual(tag.title, 'a')
        tag.delete()

        access.delete()

    def test_update_with_no_access(self):
        tag = self.create_tag('a', project=self.other_project)
        url = self._url.format(pk=tag.id)

        data = {'title': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        tag.refresh_from_db()
        self.assertEqual(tag.title, 'a')
        tag.delete()


class DeleteTagTestCase(FuglViewTestCase):

    _url = '/tags/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.tag = self.create_tag('my-tag', project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_delete_success(self):
        tags = self.project.tag_set.count()
        url = self._url.format(pk=self.tag.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.project.tag_set.count(), tags - 1)

    def test_delete_nonexistent(self):
        url = self._url.format(pk=-1)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)

    def test_delete_with_edit_access(self):
        tag = self.create_tag('a', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        tags = self.other_project.tag_set.count()
        url = self._url.format(pk=tag.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.other_project.tag_set.count(), tags - 1)

        access.delete()

    def test_delete_with_view_access(self):
        tag = self.create_tag('a', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        tags = self.other_project.tag_set.count()
        url = self._url.format(pk=tag.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.other_project.tag_set.count(), tags)

        access.delete()
        tag.delete()

    def test_delete_with_no_access(self):
        tag = self.create_tag('a', project=self.other_project)
        tags = self.other_project.tag_set.count()
        url = self._url.format(pk=tag.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.project.tag_set.count(), tags)


class AvailableTagTestCase(FuglViewTestCase):

    url = '/tags/available/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.tag = self.create_tag('test-tag', project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.tag.delete()
        self.project.delete()
        self.other_user.delete()

        super().tearDown()

    def test_available_for_available(self):
        data = {
            'project': self.project.id,
            'title': 'some-other-tag',
        }

        resp = self.client.get(self.url, data=data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertTrue(data['available'])

    def test_available_for_taken(self):
        data = {
            'project': self.project.id,
            'title': 'test-tag',
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
