from django.contrib import admin
from .models import CustomUser, FavoriteRecipes, ShoppingCart


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


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    filter_horizontal = ('subscriptions', 'groups')

    fieldsets = (
        ('About User', {
            'fields': ('username', 'email', 'first_name',
                       'last_name', 'password')
        }),
        ('Subscriprions', {
            'fields': ('subscriptions',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff',
                       'is_superuser', 'groups')
        }),
        ('Last Login', {
            'fields': ('date_joined',)
        })
    )

    inlines = [FavoriteRecipesAdminInline, ShoppingCartAdminInline]
