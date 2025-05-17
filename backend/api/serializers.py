from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, Recipe, RecipeIngredient


User = get_user_model()


class StrictBase64ImageField(Base64ImageField):
    def to_internal_value(self, data):
        if data == '':
            raise serializers.ValidationError('This field is required.')
        return super().to_internal_value(data)


class ShortRecipesSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    avatar = StrictBase64ImageField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriptions.filter(id=obj.id).exists()
        return False


class SubscriptionsUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes',
                                               'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()

        if limit and limit.isdigit() and int(limit) >= 0:
            recipes = recipes[:int(limit)]

        serializers = ShortRecipesSerializer(
            recipes,
            many=True,
            context={'request': request}
        )

        return serializers.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
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
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    def validate(self, value):
        if not Ingredient.objects.filter(
            pk=value['ingredient']['id']
        ).exists():
            raise serializers.ValidationError(
                f'Ingredient with {value['ingredient']['id']}'
                ' not exists'
            )
        return value


class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = StrictBase64ImageField()

    class Meta:
        model = Recipe
        fields = ['ingredients', 'name', 'image', 'text',
                  'cooking_time']

    def validate_ingredients(self, value):
        ids = [item['ingredient']['id'] for item in value]
        if len(ids) == 0:
            raise serializers.ValidationError(
                'Ingredients is empty.'
            )
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Ingredient is repeat.'
            )

        return value

    def add_recipe_ingredients(self, instance, ingredients):
        ingredients_ids = [item['ingredient']['id'] for item in ingredients]
        ingredients_queryset = Ingredient.objects.in_bulk(ingredients_ids)

        ingredients_links = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredients_queryset[item['ingredient']['id']],
                amount=item['amount']
            ) for item in ingredients
        ]

        RecipeIngredient.objects.bulk_create(ingredients_links)

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')

        validated_data['author'] = request.user
        recipe = Recipe.objects.create(**validated_data)

        self.add_recipe_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        instance.ingredients.all().delete()
        self.add_recipe_ingredients(instance, ingredients_data)

        return super().update(instance, validated_data)
