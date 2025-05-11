from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import SubscriptionsUserSerializer
from django.contrib.auth import get_user_model


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

