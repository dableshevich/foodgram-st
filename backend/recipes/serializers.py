from rest_framework import serializers
from api.serializers import Base64ImageField
from .models import Ingredient, Recipe, RecipeIngredient
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
    
    def validate(self, value):
        try:
            ingredient = Ingredient.objects.get(
                pk=value['ingredient']['id']
            )
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                f'Ingredient with {value['ingredient']['id']}'
                ' not exists'
            )
        
        if value['amount'] < 1:
            raise serializers.ValidationError(
                'Amount must be greater then one.'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('author', 'is_favourited',
                            'is_in_shopping_cart')
    
    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Ingredients is empty.'
            )
        ids = [item['ingredient']['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Ingredient is repeat.'
            )

        return value
    
    def validate(self, value):
        if 'ingredients' not in value:
            raise serializers.ValidationError(
                'Ingredients is required.'
            )
        return super().validate(value)
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(pk=request.user.id).exists()
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return obj.shopping_cart.filter(pk=request.user.id).exists()

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')

        validated_data['author'] = request.user
        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients_data:
            ingredient = Ingredient.objects.get(pk=item['ingredient']['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=item['amount']
            )
    
        return recipe
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        ingredients_data = validated_data.get('ingredients', None)
        if ingredients_data:
            instance.clear_ingredients()
            for item in ingredients_data:
                ingredient = Ingredient.objects.get(pk=item['ingredient']['id'])
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=item['amount']
                )
        
        instance.save()
        return instance
