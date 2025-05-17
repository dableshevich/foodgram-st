from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientViewSet, RecipeViewSet


router_recipes = DefaultRouter()
router_recipes.register('ingredients', IngredientViewSet)
router_recipes.register('recipes', RecipeViewSet)

router_users = DefaultRouter()
router_users.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router_recipes.urls)),
    path('', include(router_users.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
