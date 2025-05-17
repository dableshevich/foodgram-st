from rest_framework import viewsets, status
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from io import BytesIO
from django.db.models import Sum

from recipes.models import Ingredient, Recipe, RecipeIngredient
from users.models import ShoppingCart, FavoriteRecipes
from .serializers import (IngredientSerializer, RecipeWriteSerializer,
                          RecipeReadSerializer, ShortRecipesSerializer,
                          SubscriptionsUserSerializer)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthor


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(
        methods=['get', 'put', 'patch', 'delete'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path=('me/avatar'),
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'PUT':
            if not request.data.get('avatar'):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            response = self.partial_update(request, *args, **kwargs)
            response.data = {'avatar': response.data.get('avatar')}
            return response
        elif request.method == 'DELETE':
            user = request.user
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = user.subscriptions.all()

        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsUserSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        sub_user = self.get_object()

        if user.id == id or user == sub_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_in_subscriptions = user.subscriptions.filter(
            id=sub_user.id
        ).exists()

        if request.method == 'POST':
            if user_in_subscriptions:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            user.subscriptions.add(sub_user)
            serializer = SubscriptionsUserSerializer(
                sub_user, context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            if not user_in_subscriptions:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.subscriptions.remove(sub_user)
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthor, IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        read_serializer = RecipeReadSerializer(
            serializer.instance,
            context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        read_serializer = RecipeReadSerializer(
            serializer.instance,
            context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        recipe_in_shopping_cart = user.shopping_cart.filter(
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if recipe_in_shopping_cart:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            ShoppingCart.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = ShortRecipesSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            if not recipe_in_shopping_cart:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.shopping_cart.filter(recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        data = RecipeIngredient.objects.filter(
            recipe__in=request.user.shopping_cart.values('recipe')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        return self.create_pdf_file(data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        recipe_in_favorite = user.favorite_recipes.filter(
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if recipe_in_favorite:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            FavoriteRecipes.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = ShortRecipesSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            if not recipe_in_favorite:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.favorite_recipes.filter(recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        url_path=('get-link')
    )
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        host_path = request.get_host()
        full_path = 'http://' + host_path + f'/s/{hex(recipe.id)[2:]}'

        data = {
            'short-link': full_path
        }
        return Response(data)

    def create_pdf_file(self, data):
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
        buffer = BytesIO()

        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setFont('DejaVu', 14)

        y = 800
        pdf.drawString(100, y, 'Список покупок:')

        for item in data:
            y -= 15
            line = (
                f'- {item['ingredient__name']}: {item['total_amount']} '
                f'{item['ingredient__measurement_unit']}'
            )

            pdf.drawString(110, y, line)

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        return HttpResponse(
            buffer,
            content_type='application/pdf',
            headers={
                'Content-Disposition': (
                    'attachment; filename="shopping_list.pdf"'
                )
            }
        )

    def redirect_to_recipe(self, s_id=None):
        return redirect(f'/recipes/{int(s_id, 16)}/')
