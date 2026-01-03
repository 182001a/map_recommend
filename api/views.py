from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CourseTemplateSerializer,
    WalkSessionSerializer,
    UserPrivacyMaskSerializer
)
from .models import (
    CustomUser,
    CourseTemplate,
    WalkSession,
    UserPrivacyMask
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

# 1. コーステンプレート（計画・提案）
class CourseTemplateViewSet(viewsets.ModelViewSet):
    """
    AI提案またはユーザー保存のコーステンプレート
    """
    serializer_class = CourseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 「自分のもの」または「公開されているもの」を表示
        user = self.request.user
        return CourseTemplate.objects.filter(
            Q(user=user) | Q(is_public=True)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 2. 散歩ログ（実績）
class WalkSessionViewSet(viewsets.ModelViewSet):
    """
    実際の歩行ログの記録
    """
    serializer_class = WalkSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 自分のログのみ（セキュリティ担保）
        return WalkSession.objects.filter(user=self.request.user).order_by('-start_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 3. プライバシーエリア設定
class UserPrivacyMaskViewSet(viewsets.ModelViewSet):
    """
    自宅周辺などの非公開エリア設定
    """
    serializer_class = UserPrivacyMaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPrivacyMask.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)