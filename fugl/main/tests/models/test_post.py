from django.utils import timezone

from main.models import Category
from main.models import Post
from main.models import Project

from .helpers import parse_markdown
from ..base import FuglTestCase


class PostTestCase(FuglTestCase):

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
        self.assertEqual(self.post.filename, 'post1')

    def test_get_markdown(self):
        md = self.post.get_markdown()
        frontmatter, content = parse_markdown(md)
        date_fmt = '%Y-%m-%d'
        self.assertEqual(frontmatter.get('Title', ''), self.post.title)
        self.assertEqual(frontmatter.get('Author', ''), self.post.project.owner.username)
        self.assertEqual(frontmatter.get('Date', ''), self.post.date_created.strftime(date_fmt))
        self.assertEqual(frontmatter.get('Modified', ''), self.post.date_updated.strftime(date_fmt))
        self.assertEqual(content, self.post.content)
