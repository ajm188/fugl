import json

from ..base import FuglViewTestCase


class ListPostTestCase(FuglViewTestCase):

    url = '/posts/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('project', 'descr',
            owner=self.admin_user)
        self.post1 = self.create_post('post1', content='content',
            project=self.project)
        self.post2 = self.create_post('post2', content='content',
            project=self.project)

        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other', 'descr',
            owner=self.other_user)
        self.post3 = self.create_post('post3', content='content',
            project=self.other_project)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.other_project.delete()
        self.other_user.delete()
        self.post1.delete()
        self.post2.delete()
        self.post3.delete()
        self.project.delete()

        super().tearDown()

    def test_list(self):
        data = {'project': self.project.id}

        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), self.project.post_set.count())
        post1 = data[0]
        self.assertEqual(post1.get('title', None), self.post1.title)

    def test_list_with_edit_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {'project': self.other_project.id}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('title', None), self.post3.title)

        access.delete()

    def test_list_with_view_access(self):
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {'project': self.other_project.id}
        resp = self.client.get(self.url, data)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('title', None), self.post3.title)

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


class UpdatePostTestCase(FuglViewTestCase):

    _url = '/posts/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.post = self.create_post('my-post', 'blah',
            project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_update_success(self):
        url = self._url.format(pk=self.post.id)
        date_updated = self.post.date_updated
        resp = self.client.get(url)
        # have to check that date_updated changes!
        updated_time = resp.data['date_updated']

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data.get('title'), 'new-title')
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'new-title')
        self.assertNotEqual(data['date_updated'], updated_time)

        # undo the update
        self.post.title = 'my-post'
        self.post.date_updated = date_updated
        self.post.save()

    def test_update_bad_data(self):
        url = self._url.format(pk=self.post.id)

        data = {'title': ''}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertEqual(self.post.title, 'my-post')

    def test_update_nonexistent(self):
        url = self._url.format(pk=-1)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_update_with_edit_access(self):
        post = self.create_post('a', 'b', project=self.other_project)
        url = self._url.format(pk=post.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        data = {'content': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        post.refresh_from_db()
        self.assertEqual(post.content, 'blargh')
        post.delete()

        access.delete()

    def test_update_with_view_access(self):
        post = self.create_post('a', 'b', project=self.other_project)
        url = self._url.format(pk=post.id)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        data = {'content': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        post.refresh_from_db()
        self.assertEqual(post.content, 'b')
        post.delete()

        access.delete()

    def test_update_with_no_access(self):
        post = self.create_post('a', 'b', project=self.other_project)
        url = self._url.format(pk=post.id)

        data = {'content': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        post.refresh_from_db()
        self.assertEqual(post.content, 'b')
        post.delete()


class DeletePostTestCase(FuglViewTestCase):

    _url = '/posts/{pk}/'

    def setUp(self):
        super().setUp()

        self.project = self.create_project('admin-project',
            owner=self.admin_user)
        self.post = self.create_post('my-page', 'blah',
            project=self.project)
        self.other_user = self.create_user('other')
        self.other_project = self.create_project('other-project',
            owner=self.other_user)

        self.login(user=self.admin_user)

    def test_delete_success(self):
        posts = self.project.post_set.count()
        url = self._url.format(pk=self.post.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.project.post_set.count(), posts - 1)

    def test_delete_nonexistent(self):
        url = self._url.format(pk=-1)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)

    def test_delete_with_edit_access(self):
        post = self.create_post('a', 'b', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=True)

        posts = self.other_project.post_set.count()
        url = self._url.format(pk=post.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(self.other_project.post_set.count(), posts - 1)

        access.delete()

    def test_delete_with_view_access(self):
        post = self.create_post('a', 'b', project=self.other_project)
        access = self.create_access(self.admin_user, self.other_project,
            can_edit=False)

        posts = self.other_project.post_set.count()
        url = self._url.format(pk=post.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.other_project.post_set.count(), posts)

        access.delete()
        post.delete()

    def test_delete_with_no_access(self):
        post = self.create_post('a', 'b', project=self.other_project)
        posts = self.other_project.post_set.count()
        url = self._url.format(pk=post.id)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self.project.post_set.count(), posts)
