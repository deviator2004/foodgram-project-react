import base64
import re

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.validators import tags_ingredients_validator
from recipes.models import (Ingredients, IngredientsAmount, Recipes, Tags,
                            TagsRecipes)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.follower.filter(following=obj).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):

    def validate_username(self, value):
        if not re.fullmatch(r'^[\w.@+-]+', value):
            raise serializers.ValidationError('Запрещенные символы в username')
        return value


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'

    def to_internal_value(self, data):
        return {'id': data}


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsAmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')

    def to_internal_value(self, data):
        return data

    def to_representation(self, instance):
        ingredient = super().to_representation(instance)
        ingredient['id'] = (instance.ingredient.id)
        ingredient['name'] = (instance.ingredient.name)
        ingredient['measurement_unit'] = (instance.ingredient.measurement_unit)
        return ingredient


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientsAmountSerializer(many=True, source='amounts')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        validators = [
            UniqueTogetherValidator(
                queryset=Recipes.objects.all(),
                fields=('name', 'author'),
                message='Вы уже создавали рецепт с таким названием'
            )
        ]

    def validate_tags(self, value):
        return tags_ingredients_validator('тег', Tags, value)

    def validate_ingredients(self, value):
        value = tags_ingredients_validator('ингредиент', Ingredients, value)
        for ingredient in value:
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError('Количество не может быть '
                                                  'меньше 1')
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amounts')
        recipe = Recipes.objects.create(**validated_data)
        TagsRecipes.objects.bulk_create(
            [TagsRecipes(
                recipe=recipe,
                tag=Tags.objects.get(id=tag['id'])
            ) for tag in tags]
        )
        IngredientsAmount.objects.bulk_create(
            [IngredientsAmount(
                recipe=recipe,
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.image)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        tag_list = []
        tags_data = validated_data.pop('tags')
        for tag in tags_data:
            current_tag = Tags.objects.get(id=tag['id'])
            tag_list.append(current_tag)
        instance.tags.set(tag_list)
        ingredients_data = validated_data.pop('amounts')
        instance.ingredients.clear()
        IngredientsAmount.objects.bulk_create(
            [IngredientsAmount(
                recipe=instance,
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients_data])
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.in_favorited.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.in_shopping_cart.filter(recipe=obj).exists()
        return False


class ShortRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UserSubscribeSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit is not None and len(recipes) > int(limit):
            recipes = recipes[:int(limit)]
        return ShortRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
