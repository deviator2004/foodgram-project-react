from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import Ingredients, Recipes, Tags


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):

    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)


class IngredientsResourse(resources.ModelResource):

    class Meta:
        model = Ingredients


@admin.register(Ingredients)
class IngredientsAdmin(ImportExportModelAdmin):

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    resource_classes = [IngredientsResourse]
    ordering = ('name',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):

    list_display = ('name',)
