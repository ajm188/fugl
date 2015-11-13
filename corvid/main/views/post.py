from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from main.models import Project, Post
from .protected_view import ProtectedViewMixin
from datetime import datetime


class CreatePostView(ProtectedViewMixin, CreateView):
    template_name = 'edit_page_post.html'
    model = Post
    fields = ['title', 'category', 'content']

    def get_context_data(self, **kwargs):
        context = super(CreatePostView, self).get_context_data(**kwargs)
        context['action'] = 'Add'
        context['type'] = 'Post'
        context['project'] = self.kwargs['title']
        return context

    def form_valid(self, form):
        project = Project.objects.get(owner=self.request.user, title=self.kwargs['title'])
        data = form.cleaned_data

        now = datetime.now()
        kwargs = {
            'title': data['title'],
            'content': data['content'],
            'date_created': now,
            'date_updated': now,
            'project': project,
            'category': data['category'],
        }
        post = Post.objects.create(**kwargs)
        post.save()

        url_kwargs = {
            'owner': self.request.user.username,
            'title': self.kwargs['title'],
        }
        ctx = {
            'success_message': 'Post created!',
            'return_message': 'Project home',
            'return_url': reverse('project_home', kwargs=url_kwargs),
        }
        return TemplateResponse(self.request, 'success.html', context=ctx)


class UpdatePostView(ProtectedViewMixin, UpdateView):
    template_name = 'edit_page_post.html'
    model = Post
    fields = ['title', 'content']

    def get_object(self):
        project = Project.objects.get(owner=self.request.user, title=self.kwargs['proj_title'])
        post = Post.objects.get(project=project, title=self.kwargs['post_title'])
        return post

    def get_context_data(self, **kwargs):
        context = super(UpdatePostView, self).get_context_data(**kwargs)
        context['action'] = 'Edit'
        context['type'] = 'Post'
        context['project'] = self.kwargs['proj_title']
        return context

    def get_success_url(self):
        kwargs = {
            'owner': self.request.user.username,
            'title': self.kwargs['proj_title']
        }
        return reverse('project_home', kwargs=kwargs)