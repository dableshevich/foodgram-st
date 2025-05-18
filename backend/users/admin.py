from django.contrib import admin

from .models import CustomUser, Subscriptions
from recipes.models import FavoriteRecipes, ShoppingCart


class FavoriteRecipesAdminInline(admin.TabularInline):
    model = FavoriteRecipes
    extra = 1
    autocomplete_fields = ['recipe']
    verbose_name_plural = 'Favorite Recipes'


class ShoppingCartAdminInline(admin.TabularInline):
    model = ShoppingCart
    extra = 1
    autocomplete_fields = ['recipe']
    verbose_name_plural = 'Shopping Cart'


class SubscriptionsAdminInline(admin.TabularInline):
    model = Subscriptions
    extra = 1
    fk_name = 'user'
    autocomplete_fields = ['subscribe']
    verbose_name_plural = 'Subsciprions'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['username']
    list_display = ['username', 'email']
    filter_horizontal = ['groups']

    fieldsets = (
        ('About User', {
            'fields': ('username', 'email', 'first_name',
                       'last_name', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff',
                       'is_superuser', 'groups')
        }),
        ('Last Login', {
            'fields': ('date_joined',)
        })
    )

    inlines = [FavoriteRecipesAdminInline, ShoppingCartAdminInline,
               SubscriptionsAdminInline]


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    pass
