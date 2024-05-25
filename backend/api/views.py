from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientsFilter, RecipesFilter
from api.permissions import IsStaffAuthorOrReadOnly
from api.serializers import (IngredientsSerializer, RecipeReadSerializer,
                             RecipesSerializer, ShortRecipesSerializer,
                             TagsSerializer, UserSubscribeSerializer)
from recipes.models import (Ingredients, IngredientsAmount, Recipes,
                            RecipesIsFavorited, RecipesIsInShoppingCart,
                            Subscriptions, Tags)

User = get_user_model()


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsStaffAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            serializer_class = RecipeReadSerializer
        else:
            serializer_class = RecipesSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['partial'] = False
        return serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def favorite_shopping_cart_create(self, request, pk, Model, errors):
        if not Recipes.objects.filter(pk=pk).exists():
            return Response(
                {'error': f'Нет рецепта с id {pk}'},
                status=status.HTTP_404_NOT_FOUND
            )
        recipe = Recipes.objects.get(pk=pk)
        user = request.user
        in_list = Model.objects.filter(
            user=user, recipe=recipe
        ).exists()
        if in_list:
            return Response(
                {'error': errors['post_error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        Model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def favorite_shopping_cart_delete(self, request, pk, Model, errors):
        if not Recipes.objects.filter(pk=pk).exists():
            return Response(
                {'error': f'Нет рецепта с id {pk}'},
                status=status.HTTP_404_NOT_FOUND
            )
        recipe = Recipes.objects.get(pk=pk)
        user = request.user
        in_list = Model.objects.filter(
            user=user, recipe=recipe
        ).exists()
        if not in_list:
            return Response(
                {'error': errors['delete_error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        Model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        Model = RecipesIsFavorited
        errors = {
            'post_error': 'Рецепт уже в избранном',
        }
        return self.favorite_shopping_cart_create(request, pk, Model, errors)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        Model = RecipesIsFavorited
        errors = {
            'delete_error': 'Рецепта нет в избранном'
        }
        return self.favorite_shopping_cart_delete(request, pk, Model, errors)

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        Model = RecipesIsInShoppingCart
        errors = {
            'post_error': 'Рецепт уже в списке покупок',
        }
        return self.favorite_shopping_cart_create(request, pk, Model, errors)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        Model = RecipesIsInShoppingCart
        errors = {
            'delete_error': 'Рецепта нет в списке покупок'
        }
        return self.favorite_shopping_cart_delete(request, pk, Model, errors)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipes.objects.filter(in_shopping_cart__user=user)
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


class UserSubscribesViewSet(UserViewSet):

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscribeslist = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(subscribeslist)
        serializer = UserSubscribeSerializer(pages, many=True)
        serializer.context['request'] = request
        return self.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        following = get_object_or_404(User, id=id)
        is_subcribe = Subscriptions.objects.filter(
            user=user,
            following=following
        ).exists()
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
        context = {'request': request}
        serializer = UserSubscribeSerializer(following, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        following = get_object_or_404(User, id=id)
        is_subcribe = Subscriptions.objects.filter(
            user=user,
            following=following
        ).exists()
        if not is_subcribe:
            return Response(
                {'error': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.get(user=user, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
