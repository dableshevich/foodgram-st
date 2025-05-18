from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from . import constants


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=constants.INGREDIENT_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Name'
    )
    measurement_unit = models.CharField(
        max_length=constants.INGREDIENT_MEASUREMENT_MAX_LENGTH,
        verbose_name='Measurement unit'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name="unique_name_measurement_unit"
            )
        ]
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
        verbose_name='Name'
    )
    text = models.TextField(
        verbose_name='Description'
    )
    cooking_time = models.IntegerField(
        validators=(
            MinValueValidator(constants.MIN_INTEGER_VALUE),
        ),
        verbose_name='Cooking time'
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='recipes/'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
        related_name='recipes'
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    amount = models.IntegerField(
        validators=(
            MinValueValidator(constants.MIN_INTEGER_VALUE),
        ),
        verbose_name='Amount'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name="unique_recipe_ingredient"
            )
        ]


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_user_recipe_favorite_recipes"
            )
        ]

    def __str__(self):
        return self.user.name


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_user_recipe_shopping_cart"
            )
        ]

    def __str__(self):
        return self.user.name
