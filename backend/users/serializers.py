from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.serializers import Base64ImageField, ShortRecipesSerializer


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()
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
