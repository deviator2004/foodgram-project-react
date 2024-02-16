from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import IngredientsViewSet, RecipesViewSet, TagsViewSet


router = DefaultRouter()
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
