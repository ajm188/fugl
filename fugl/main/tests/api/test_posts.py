import json
from unittest import skip

from ..base import FuglViewTestCase


class CreatePostTestCase(FuglViewTestCase):

    url = '/posts/'

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
        posts_count = self.project.post_set.count()
        data = {
            'project': self.project.id,
            'title': 'my-post',
            'content': 'post content',
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertEqual(data.get('title'), 'my-post')
        self.assertEqual(data.get('content'), 'post content')
        self.assertIn('date_created', data)
        self.assertIn('date_updated', data)
        self.assertEqual(data['date_created'], data['date_updated'])

        self.assertEqual(posts_count + 1, self.project.post_set.count())

        [p.delete() for p in self.project.post_set.all()]

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

        self.other_project.post_set.all()[0].delete()
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


class RetrievePostTestCase(FuglViewTestCase):

    _url = '/posts/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.post = self.create_post('test-post', 'post-content',
            project=self.project)
        self.url = self._url.format(pk=self.post.id)

        self.user = self.create_user('user')
        self.login(user=self.user, password='user')

    def tearDown(self):
        self.post.delete()
        self.project.delete()
        self.user.delete()

        super().tearDown()

    def test_retrieve_with_view_access_success(self):
        access = self.create_access(self.user, self.project)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertIn('title', data)
        self.assertEqual(data['title'], self.post.title)
        self.assertIn('content', data)
        self.assertEqual(data['content'], self.post.content)

        access.delete()

    def test_retrieve_with_no_access_fail(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)

        url = self._url.format(pk=-1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
