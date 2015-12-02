from django.db import models


class ProjectPlugin(models.Model):
    class Meta:
        unique_together = (('title', 'project'),)
        index_together = (('title', 'project'),)

    title = models.CharField(max_length=50)
    markup = models.CharField(max_length=5000)

    project = models.ForeignKey('Project')

    def clone(self, newproject):
        kwargs = {
            'title': self.title,
            'markup': self.markup,
            'project': newproject,
        }
        new = ProjectPlugin.objects.create(**kwargs)
        new.save()
        return new
