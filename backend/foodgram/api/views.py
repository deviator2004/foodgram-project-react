from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from recipes.models import Ingredients, Recipes, Tags
from api.filters import RecipesFilter
from api.serializers import (IngredientsSerializer, RecipesSerializer,
                             TagsSerializer)
from api.permissions import IsStaffAuthorOrReadOnly


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsStaffAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def get_serializer_class(self):
    #     if self.request.method == 'GET':
    #         return RecipesReadSerializer
    #     return RecipesSerializer
