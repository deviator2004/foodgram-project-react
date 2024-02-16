from django_filters import rest_framework as filters

from recipes.models import Recipes


class RecipesFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorited_cart'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_favorited_cart'
    )
    author = filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='icontains'
    )

    class Meta:
        model = Recipes
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_favorited_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            lookup = '__'.join([name, 'user'])
            return queryset.filter(**{lookup: self.request.user})
        return queryset

    # def filter_is_favorited(self, queryset, name, value):
    #     if value and self.request.user.is_authenticated:
    #         return queryset.filter(is_favorited__user=self.request.user)
    #     return queryset

    # def filter_is_shopping_cart(self, queryset, name, value):
    #     if value and self.request.user.is_authenticated:
    #         return queryset.filter(is_shopping_cart__user=self.request.user)
    #     return queryset
