from django.contrib import admin

from recipes.models import Ingredients, Recipes, Tags


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):

    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):

    list_display = ('name',)
