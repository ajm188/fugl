import json

from ..base import FuglViewTestCase


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
