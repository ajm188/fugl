from main.models import ProjectAccess


class UserAccess(object):

    def __init__(self, user):
        self.user = user

    def can_edit(self, project):
        return self.__access_helper(project,
            if_found=lambda access: access.can_edit)

    def can_view(self, project):
        return self.__access_helper(project, if_found=lambda _: True)

    def __access_helper(self, project, if_found=lambda _: False):
        if project.owner == self.user:
            return True

        try:
            access = ProjectAccess.objects.get(
                user=self.user,
                project=project,
            )
            return if_found(access)
        except ProjectAccess.DoesNotExist:
            return False
