from django.contrib import admin
from .models import Recipe, RecipeIngredient, Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ['name']


class RecipeIngredientAdminInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']
    verbose_name_plural = 'Ingredients'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'cooking_time',
                    'image', 'author')

    fieldsets = (
        ('About recipe', {
            'fields': ('name', 'text', 'cooking_time',
                       'image', 'author')
        }),
    )
    inlines = [RecipeIngredientAdminInline]
