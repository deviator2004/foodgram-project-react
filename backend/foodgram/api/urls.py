from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import TagsViewSet


router = DefaultRouter()
router.register('tags', TagsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
