from django.views.generic import ListView

from main.models import Project
from main.models import ProjectAccess

from .protected_view import ProtectedViewMixin

class UserHomeView(ProtectedViewMixin, ListView):
    """View that will list all projects belonging to this User"""
    model = Project
    template_name = 'account_home.html'

    def get_queryset(self):
        """Get all projects that belong to this user"""
        return Project.objects.filter(owner=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(UserHomeView, self).get_context_data(*args, **kwargs)
        context['project_access_list'] = self.get_project_accesses()
        return context

    def get_project_accesses(self):
        user = self.request.user
        accesses = \
            ProjectAccess.objects.filter(user=user)
        return accesses
