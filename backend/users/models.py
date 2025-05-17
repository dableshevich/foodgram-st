from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, UserManager
from . import constants


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=constants.EMAIL_MAX_LENGTH,
        verbose_name='Email'
    )
    username = models.CharField(
        unique=True,
        max_length=constants.USERNAME_MAX_LENGTH,
        verbose_name='Username',
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username is not valid'
        )]
    )
    first_name = models.CharField(
        max_length=constants.FIRST_AND_LAST_NAMES_MAX_LENGTH,
        verbose_name='First name'
    )
    last_name = models.CharField(
        max_length=constants.FIRST_AND_LAST_NAMES_MAX_LENGTH,
        verbose_name='Last name'
    )
    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscribers',
        blank=True,
        verbose_name='Subsribers'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    EMAIL_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        verbose_name = 'Favorite Recipes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_user_recipe_favorite_recipes"
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_user_recipe_shopping_cart"
            )
        ]
