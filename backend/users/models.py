from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
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
        max_length=254,
        verbose_name='Email'
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Username',
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username is not valid'
        )]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='First name'
    )
    last_name = models.CharField(
        max_length=150,
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
    favorite_recipes = models.ManyToManyField(
        'recipes.Recipe',
        related_name='favorited_by',
        blank=True,
        verbose_name='Favourite Recipes'
    )
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        related_name='shopping_cart',
        blank=True,
        verbose_name='Shopping Cart'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    EMAIL_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.username