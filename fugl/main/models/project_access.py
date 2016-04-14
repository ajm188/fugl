from django.db import models

from .project import Project
from .user import User


class ProjectAccess(models.Model):

    class Meta:
        unique_together = (('user', 'project'),)
        index_together = (('user', 'project'),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
