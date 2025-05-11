from .models import Ingredient, Recipe
import django_filters


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    author = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['author']
    
    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or value not in (1, 0):
            return queryset
        if value:
            return queryset.filter(favorited_by=user)
        else:
            return queryset.exclude(favorited_by=user)
    
    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or value not in (1, 0):
            return queryset
        if value:
            return queryset.filter(shopping_cart=user)
        else:
            return queryset.exclude(shopping_cart=user)
