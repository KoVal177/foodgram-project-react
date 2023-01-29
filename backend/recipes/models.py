from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

MIN_COOKING_TIME_MINUTES = 1
MIN_AMOUNT_INGREDIENT_UNITS = 0


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=100,
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
    )
    slug = models.SlugField(
        'Адрес',
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return str(self.slug)


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=50,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self) -> str:
        return '{}, {}'.format(self.name, self.measurement_unit)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=300,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientAmount',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME_MINUTES,
                message='Время приготовления должно быть не менее 1 мин.'
            ),
        ),
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return str(self.name)


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='amounts',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='amounts'
    )
    amount = models.PositiveIntegerField(
        'Количество продукта',
        validators=(
            MinValueValidator(
                MIN_AMOUNT_INGREDIENT_UNITS,
                message='Количество не может быть меньше {}.'.format(
                    MIN_AMOUNT_INGREDIENT_UNITS
                )
            ),
        ),
    )

    class Meta:
        verbose_name = 'Количество продукта'
        verbose_name_plural = 'Количество продуктов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique ingredient amount',
            ),
        ]


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique favorites',
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique shopping cart',
            ),
        ]
