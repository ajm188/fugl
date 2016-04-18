from main.models import Project
from main.models import ProjectAccess
from main.models import User
from main.util import UserAccess

from ..base import FuglTestCase


class UserAccessTestCase(FuglTestCase):

    def setUp(self):
        super().setUpTheme()

        self.owner = User.objects.create(username='project-owner',
            password='foo')
        self.owner.save()

        self.project = Project.objects.create(title='a', description='',
            owner=self.owner, theme=self.default_theme)
        self.project.save()

    def tearDown(self):
        super().tearDownTheme()
        self.project.delete()
        self.owner.delete()

    def test_owner_can_view_and_edit(self):
        self.assertTrue(
            UserAccess(self.owner).can_view(self.project)
        )
        self.assertTrue(
            UserAccess(self.owner).can_edit(self.project)
        )

    def test_user_with_edit_can_view_and_edit(self):
        user_with_edit = User.objects.create(username='edit',
            password='foo')
        user_with_edit.save()
        ProjectAccess.objects.create(user=user_with_edit,
            project=self.project, can_edit=True).save()

        self.assertTrue(
            UserAccess(user_with_edit).can_view(self.project)
        )
        self.assertTrue(
            UserAccess(user_with_edit).can_edit(self.project)
        )
        user_with_edit.delete()

    def test_user_with_view_can_view_but_not_edit(self):
        user_with_view = User.objects.create(username='view',
            password='foo')
        user_with_view.save()
        ProjectAccess.objects.create(user=user_with_view,
            project=self.project, can_edit=False).save()

        self.assertTrue(
            UserAccess(user_with_view).can_view(self.project)
        )
        self.assertFalse(
            UserAccess(user_with_view).can_edit(self.project)
        )
        user_with_view.delete()

    def test_other_user_cannot_view_or_edit(self):
        other = User.objects.create(username='other', password='foo')
        other.save()

        self.assertFalse(
            UserAccess(other).can_view(self.project)
        )
        self.assertFalse(
            UserAccess(other).can_edit(self.project)
        )
        other.delete()
