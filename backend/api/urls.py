from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientsViewSet, RecipesViewSet, TagsViewSet,
                       UserSubscribesViewSet)

router = DefaultRouter()
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('users', UserSubscribesViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
