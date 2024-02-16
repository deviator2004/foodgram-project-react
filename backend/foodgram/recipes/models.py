from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


class BaseTagsIngredientsRecipesModel(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.LIMIT_NAME,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ("name",)


class Tags(BaseTagsIngredientsRecipesModel):
    color = ColorField(default='#FF0000')
    slug = models.SlugField(
        'Слаг',
        max_length=settings.LIMIT_SLUG,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(BaseTagsIngredientsRecipesModel):
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.LIMIT_SLUG
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipes(BaseTagsIngredientsRecipesModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes/images/',
    )
    text = models.TextField('Описание приготовления блюда')
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsAmount',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Теги',
        through='TagsRecipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(1, message='Время приготовления'
                              'не может быть меньше минуты')
        ]
    )
    is_favorited = models.ManyToManyField(
        User,
        related_name='favorited',
        through='RecipesIsFavorited'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        through='RecipesIsInShoppingCart'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipes'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_name_author'
            )
        ]

    def __str__(self):
        return self.name[:settings.LIMIT_SELF_TEXT]


class IngredientsAmount(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(1, message='Количество не может быть меньше 1')
        ]
    )

    class Meta:
        default_related_name = 'amounts'
        unique_together = ('ingredient', 'recipe')


class TagsRecipes(models.Model):
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tag', 'recipe')


class BaseFavoritedShoppingCartModel(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        unique_together = ('user', 'recipe')


class RecipesIsFavorited(BaseFavoritedShoppingCartModel):

    class Meta:
        default_related_name = 'in_favorited'


class RecipesIsInShoppingCart(BaseFavoritedShoppingCartModel):

    class Meta:
        default_related_name = 'in_shopping_cart'


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    following = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'подписка'
        unique_together = ('user', 'following')
