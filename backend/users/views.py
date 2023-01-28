from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import (IsAuthenticated, 
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import CustomPageNumberPagination
from .models import Follow, User
from .serializers import CustomUserSerializer, FollowSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FollowViewSet(APIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))
        if author.id == request.user.id:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Follow.objects.filter(
            user=request.user,
            author_id=author.id
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Follow.objects.create(
            user=request.user,
            author_id=author.id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user.id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на автора'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowListView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

