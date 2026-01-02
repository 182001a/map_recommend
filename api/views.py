from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import (
    UserSerializer,
    RegisterSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    ユーザー登録
    POST /api/auth/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    """
    ログイン（Token発行）
    POST /api/auth/login/
    body: { "username": "...", "password": "..." }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "username と password は必須です。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "認証に失敗しました。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveAPIView):
    """
    ログイン中ユーザー情報
    GET /api/auth/me/
    Authorization: Token <token>
    """
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
