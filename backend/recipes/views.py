from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer
from .models import Ingredient, Recipe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from api.serializers import ShortRecipesSerializer
from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from io import BytesIO


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        recipe_in_shopping_cart = user.shopping_cart.filter(
            id=recipe.id
        ).exists()

        if request.method == 'POST':
            if recipe_in_shopping_cart:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            user.shopping_cart.add(recipe)
            serializer = ShortRecipesSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            if not recipe_in_shopping_cart:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        recipes = request.user.shopping_cart.all()
        data = dict()

        for item in recipes:
            for ingredient in item.ingredients.all():
                ing_name = ingredient.ingredient.name
                if ing_name not in data:
                    data[ing_name] = {
                        'amount': ingredient.amount,
                        'unit': ingredient.ingredient.measurement_unit
                    }
                else:
                    data[ing_name]['amount'] += ingredient.amount
        
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
            id=recipe.id
        ).exists()

        if request.method == 'POST':
            if recipe_in_favorite:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            user.favorite_recipes.add(recipe)
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
            user.favorite_recipes.remove(recipe)
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

        for key, value in data.items():
            y -= 15
            line = (
                f'- {key}: {value['amount']} '
                f'{value['unit']}'
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
        
