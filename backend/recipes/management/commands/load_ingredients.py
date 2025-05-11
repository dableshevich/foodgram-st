import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из JSON в базу данных'

    def handle(self, *args, **options):
        with open('data/ingredients.json', 'r', encoding='utf-8') as ingredients_data:
            ingredients = json.load(ingredients_data)
            
            for item in ingredients:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
        
        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены!'))