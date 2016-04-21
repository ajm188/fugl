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
