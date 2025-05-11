from django.urls import path, include
from .views import IngredientViewSet, RecipeViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]