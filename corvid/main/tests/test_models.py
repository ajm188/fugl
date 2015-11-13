"""
Tests for the few model functions we have.
"""

from django.utils import timezone
from main.models import Page, Post, Project, Category
from .base import CorvidTestCase


def parse_markdown(md):
    idx = md.find('\n\n')
    prefix = md[:idx]
    suffix = md[idx+2:]
    pairs = [l.split(':', maxsplit=1) for l in prefix.splitlines()]
    pairs = [(fst.strip(), snd.strip()) for fst, snd in pairs]
    frontmatter = dict(pairs)
    return frontmatter, suffix[:-1]


class PageTestCase(CorvidTestCase):

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
        self.assertEqual(self.page.filename, 'page1.md')

    def test_get_markdown(self):
        md = self.page.get_markdown()
        frontmatter, content = parse_markdown(md)
        self.assertEqual(frontmatter.get('Title', ''), self.page.title)
        self.assertEqual(content, self.page.content)


class PostTestCase(CorvidTestCase):

    def setUp(self):
        self.setUpTheme()

        self.project = Project.objects.create(title='project',
                                              description='project',
                                              owner=self.admin_user,
                                              theme=self.default_theme)
        self.project.save()

        self.category = Category.objects.create(title='cock-of-the-rock',
                                                project=self.project)

        self.post = Post.objects.create(title='post1',
                                        content='post1',
                                        date_created=timezone.now(),
                                        date_updated=timezone.now(),
                                        category=self.category,
                                        project=self.project)
        self.post.save()

    def tearDown(self):
        self.post.delete()
        self.project.delete()
        self.tearDownTheme()

    def test_filename(self):
        self.assertEqual(self.post.filename, 'post1.md')

    def test_get_markdown(self):
        md = self.post.get_markdown()
        frontmatter, content = parse_markdown(md)
        date_fmt = '%Y-%m-%d'
        self.assertEqual(frontmatter.get('Title', ''), self.post.title)
        self.assertEqual(frontmatter.get('Author', ''), self.post.project.owner.username)
        self.assertEqual(frontmatter.get('Date', ''), self.post.date_created.strftime(date_fmt))
        self.assertEqual(frontmatter.get('Modified', ''), self.post.date_updated.strftime(date_fmt))
        self.assertEqual(content, self.post.content)
