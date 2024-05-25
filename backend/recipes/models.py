from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

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
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]

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
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(1, message='Время приготовления'
                              'не может быть меньше минуты')
        ]
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
        verbose_name = 'Ингредиенты в рецептах'
        verbose_name_plural = 'Количество ингредиентов в рецептах'
        default_related_name = 'amounts'
        unique_together = ('ingredient', 'recipe')


class BaseFavoritedShoppingCartModel(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe'
            )
        ]


class RecipesIsFavorited(BaseFavoritedShoppingCartModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Рецепты в избранном'
        default_related_name = 'in_favorited'


class RecipesIsInShoppingCart(BaseFavoritedShoppingCartModel):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Рецепты в списках покупок'
        default_related_name = 'in_shopping_cart'


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_user_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("following")),
                name='prevent_self_follow'
            )
        ]
