from rest_framework import routers

from .api import CategoryViewSet
from .api import PagePluginViewSet
from .api import PageViewSet
from .api import PostViewSet
from .api import ProjectPluginViewSet
from .api import ProjectViewSet
from .api import TagViewSet
from .api import ThemeViewSet
from .api import UserViewSet


router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'pages', PageViewSet)
router.register(r'posts', PostViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'project_plugins', ProjectPluginViewSet)
router.register(r'page_plugins', PagePluginViewSet)
router.register(r'themes', ThemeViewSet)
urlpatterns = router.urls
