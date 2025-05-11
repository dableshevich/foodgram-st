from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Name'
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Measurement unit'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Name'
    )
    text = models.TextField(
        verbose_name='Description'
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(1),),
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

    def clear_ingredients(self):
        ingredients = self.ingredients.all()
        for item in ingredients:
            item.delete()

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
    amount = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name="unique_recipe_ingredient"
            )
        ]
