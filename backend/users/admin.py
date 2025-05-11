from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    filter_horizontal = ('subscriptions', 'groups',
                         'shopping_cart', 'favorite_recipes')

    fieldsets = (
        ('About User', {
            'fields': ('username', 'email', 'first_name',
                       'last_name', 'password')
        }),
        ('Subscriprions', {
            'fields': ('subscriptions',)
        }),
        ('Shopping cart', {
            'fields': ('shopping_cart',)
        }),
        ('Favorite recipes', {
            'fields': ('favorite_recipes',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff',
                       'is_superuser', 'groups')
        }),
        ('Last Login', {
            'fields': ('date_joined',)
        })
    )
