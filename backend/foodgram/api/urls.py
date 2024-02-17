from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientsViewSet, RecipesViewSet,
                       SubscribesListViewSet, subscribe, TagsViewSet)


router = DefaultRouter()
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipesViewSet)
router.register('tags', TagsViewSet)
router.register('users/subscriptions', SubscribesListViewSet,
                basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/subscribe/', subscribe),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
