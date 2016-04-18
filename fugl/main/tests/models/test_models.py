"""
Tests for the few model functions we have.
"""

from main.models import Project

from .helpers import parse_markdown
from ..base import FuglTestCase


class ProjectTestCase(FuglTestCase):

    def setUp(self):
        self.setUpTheme()

        self.project = Project.objects.create(title='project',
                                              description='project',
                                              owner=self.admin_user,
                                              theme=self.default_theme)
        self.project.save()

    def tearDown(self):
        self.project.delete()
        self.tearDownTheme()

    def test_config(self):
        conf = self.project.get_pelican_conf()
        self.assertIn("AUTHOR = '%s'" % self.project.owner.username, conf)
        self.assertIn("SITENAME = '%s'" % self.project.title, conf)

    def test_project_home_url(self):
        url = '/project/%s/%s' % (self.project.owner.username,
                                  self.project.title)
        self.assertEqual(url, self.project.project_home_url)
