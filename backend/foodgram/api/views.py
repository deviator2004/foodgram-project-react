from django.db.models import Sum
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredients, IngredientsAmount, Recipes,
                            RecipesIsInShoppingCart, RecipesIsFavorited,
                            Subscriptions, Tags)
from api.filters import RecipesFilter
from api.serializers import (IngredientsSerializer, RecipesSerializer,
                             ShortRecipesSerializer, TagsSerializer,
                             UserSubscribeSerializer)
from api.permissions import IsStaffAuthorOrReadOnly


User = get_user_model()


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

    def favorite_shopping_cart_recipes(self, request, pk, Model, errors):
        recipe = get_object_or_404(Recipes, pk=pk)
        user = request.user
        in_list = Model.objects.filter(
            user=user, recipe=recipe
        ).exists()
        if request.method == 'POST':
            if in_list:
                return Response(
                    {'error': errors['post_error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not in_list:
            return Response(
                {'error': errors['delete_error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        Model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        Model = RecipesIsFavorited
        errors = {
            'post_error': 'Рецепт уже в избранном',
            'delete_error': 'Рецепта нет в избранном'
        }
        return self.favorite_shopping_cart_recipes(request, pk, Model, errors)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        Model = RecipesIsInShoppingCart
        errors = {
            'post_error': 'Рецепт уже в списке покупок',
            'delete_error': 'Рецепта нет в списке покупок'
        }
        return self.favorite_shopping_cart_recipes(request, pk, Model, errors)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = user.shopping_cart.all()
        ingredients = IngredientsAmount.objects.filter(
            recipe__in=recipes
        ).values('ingredient').annotate(total=Sum('amount')).values_list(
            'ingredient__name', 'total', 'ingredient__measurement_unit'
        )
        response = HttpResponse('Список покупок:\n', content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_cart.txt"')
        for ingredient in ingredients:
            response.write(f'{ingredient[0].capitalize()}: {ingredient[1]}'
                           f' {ingredient[2]}\n')
        return response


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def subscribe(request, pk=None):
    user = request.user
    following = get_object_or_404(User, id=pk)
    is_subcribe = Subscriptions.objects.filter(
        user=user,
        following=following
    ).exists()
    if request.method == 'POST':
        if is_subcribe:
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif user == following:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.create(user=user, following=following)
        serializer = UserSubscribeSerializer(following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if not is_subcribe:
        return Response(
            {'error': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )
    Subscriptions.objects.get(user=user, following=following).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribesListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = User.objects.all().prefetch_related('follower').filter(
            follower__user=self.request.user
        )
        return queryset
