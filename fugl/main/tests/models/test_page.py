from main.models import Page
from main.models import Project

from .helpers import parse_markdown
from ..base import FuglTestCase


class PageTestCase(FuglTestCase):

    def setUp(self):
        self.setUpTheme()

        self.project = Project.objects.create(title='project',
                                              description='project',
                                              owner=self.admin_user,
                                              theme=self.default_theme)
        self.project.save()

        self.page = Page.objects.create(title='page1',
                                        content='page1',
                                        project=self.project)
        self.page.save()

    def tearDown(self):
        self.page.delete()
        self.project.delete()
        self.tearDownTheme()

    def test_filename(self):
        self.assertEqual(self.page.filename, 'page1')

    def test_get_markdown(self):
        md = self.page.get_markdown()
        frontmatter, content = parse_markdown(md)
        self.assertEqual(frontmatter.get('Title', ''), self.page.title)
        self.assertEqual(content, self.page.content)
