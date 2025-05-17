import django_filters

from recipes.models import Ingredient, Recipe


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

    class Meta:
        model = Recipe
        fields = ['author']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or value not in (1, 0):
            return queryset
        if value:
            return queryset.filter(favorited_by__user=user)
        else:
            return queryset.exclude(favorited_by__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or value not in (1, 0):
            return queryset
        if value:
            return queryset.filter(shopping_cart__user=user)
        else:
            return queryset.exclude(shopping_cart__user=user)
