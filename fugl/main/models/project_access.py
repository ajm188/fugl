from django.db import models

from .project import Project
from .user import User


class ProjectAccess(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
