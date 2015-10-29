from django.conf.urls import url
from .views.root import root_controller
from .views.user import UserHomeView
from .views.registration import RegistrationView
from .views.create_project import CreateProjectView
from .views.page import CreatePageView
from .views.page import UpdatePageView
from .views.project_home import ProjectDetailView
from django.contrib.auth.views import login as login_view


urlpatterns = [
    url(r'^$', root_controller, name='root'),
    url(r'^login', login_view, name='login'),
    url(r'^home', UserHomeView.as_view(), name='home'),
    url(r'^register', RegistrationView.as_view(), name='register'),
    url(r'^project/create$', CreateProjectView.as_view(), name='new_project'),
    url(r'^project/(?P<owner>[^/]+)/(?P<title>[^/]+)/?$',
        ProjectDetailView.as_view(), name='project_home'),
    url(r'^project/(?P<owner>[^/]+)/(?P<title>[^/]+)/page/new',
        CreatePageView.as_view(), name='new_page'),
    url(r'^project/(?P<owner>[^/]+)/(?P<proj_title>[^/]+)/page/edit/(?P<page_title>[^/]+)',
        UpdatePageView.as_view(), name='edit_page'),
]
