import json

from main.models import Theme

from ..base import FuglViewTestCase


class CreateThemeTestCase(FuglViewTestCase):

    url = '/themes/'

    def setUp(self):
        super().setUp()

        self.login(user=self.admin_user)

    def test_create_success(self):
        count = Theme.objects.count()
        data = {
            'title': 'my-theme',
            'body_markup': 'some-markup',
            'filepath': '',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 201)

        data = resp.data
        self.assertIn('title', data)
        self.assertIn('body_markup', data)
        self.assertIn('filepath', data)
        self.assertIn('creator', data)

        self.assertEqual(data['creator'], self.admin_user.id)

        self.assertEqual(Theme.objects.count(), count + 1)

    def test_create_duplicate(self):
        theme1 = self.create_theme('my-theme', 'my markup')

        count = Theme.objects.count()
        data = {
            'title': 'my-theme',
            'body_markup': 'some-markup',
            'filepath': '',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertEqual(Theme.objects.count(), count)

        theme1.delete()

    def test_create_bad_data(self):
        count = Theme.objects.count()
        data = {
            'title': 'my-theme',
            'body_markup': '',
            'filepath': '',
        }

        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertIn('body_markup', resp.data)
        self.assertNotIn('title', resp.data)
        self.assertEqual(Theme.objects.count(), count)

        del data['title']
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)

        self.assertIn('body_markup', resp.data)
        self.assertIn('title', resp.data)
        self.assertEqual(Theme.objects.count(), count)


class RetrieveThemeTestCase(FuglViewTestCase):

    _url = '/themes/{pk}/'

    def setUp(self):
        super().setUp()

        self.theme = self.create_theme('test-theme', 'my markup')
        self.url = self._url.format(pk=self.theme.id)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.theme.delete()

        super().tearDown()

    def test_retrieve(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertIn('title', data)
        self.assertIn('body_markup', data)
        self.assertIn('creator', data)
        self.assertIn('filepath', data)

        self.assertEqual(data['title'], 'test-theme')
        self.assertEqual(data['body_markup'], 'my markup')

    def test_nonexistent(self):
        resp = self.client.get(self._url.format(pk=-1))
        self.assertEqual(resp.status_code, 404)


class UpdateThemeTestCase(FuglViewTestCase):

    _url = '/themes/{pk}/'

    def setUp(self):
        super().setUp()

        self.theme = self.create_theme('my-theme', 'my markup')
        self.other_user = self.create_user('other')
        self.other_theme = self.create_theme('other-theme', 'other markup',
            creator=self.other_user)

        self.login(user=self.admin_user)

    def tearDown(self):
        self.theme.delete()
        self.other_theme.delete()
        self.other_user.delete()

        super().tearDown()

    def test_update_success(self):
        url = self._url.format(pk=self.theme.id)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data.get('title'), 'new-title')
        self.theme.refresh_from_db()
        self.assertEqual(self.theme.title, 'new-title')

        # undo the update
        self.theme.title = 'my-theme'
        self.theme.save()

    def test_bad_data(self):
        url = self._url.format(pk=self.theme.id)

        data = {'title': ''}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        self.assertIn('title', resp.data)
        self.assertEqual(self.theme.title, 'my-theme')

    def test_nonexistent(self):
        url = self._url.format(pk=-1)

        data = {'title': 'new-title'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_with_unowned_theme(self):
        url = self._url.format(pk=self.other_theme.id)

        data = {'title': 'blargh'}
        resp = self.client.put(url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

        self.other_theme.refresh_from_db()
        self.assertEqual(self.other_theme.title, 'other-theme')
