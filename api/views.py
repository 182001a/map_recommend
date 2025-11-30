from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import CourseTemplate, CourseMode
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CourseTemplateSerializer,
    CourseModeSerializer,
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


class CourseModeListView(generics.ListAPIView):
    """
    利用可能なモード一覧
    GET /api/course-modes/
    例: walk(散歩), meal(食事), sightseeing(観光)
    """
    queryset = CourseMode.objects.all()
    serializer_class = CourseModeSerializer
    permission_classes = [permissions.AllowAny]


class CourseTemplateListCreateView(generics.ListCreateAPIView):
    """
    コースひな型の一覧取得＆作成

    GET  /api/course-templates/
      - ログインユーザーに関係なく is_active=True のコース一覧を返す
      - spots と modes をネストで含める

    POST /api/course-templates/
      - ユーザーが入力したコース情報をDBに保存する
      - body 例:
        {
          "title": "テストコース",
          "description": "テスト用の説明",
          "mood": "relax",
          "default_distance_m": 2500,
          "default_duration_min": 60,
          "mode_codes": ["walk", "meal"],
          "spots": [
            {
              "order": 1,
              "name": "テスト公園",
              "place_id": "user-dummy-1",
              "category": "park",
              "stay_time_min": 20,
              "lat": 35.0,
              "lng": 135.0
            },
            {
              "order": 2,
              "name": "テストカフェ",
              "place_id": "user-dummy-2",
              "category": "cafe",
              "stay_time_min": 30,
              "lat": 35.001,
              "lng": 135.001
            }
          ]
        }
      - owner にはログイン中ユーザーが自動で紐づく
    """

    queryset = CourseTemplate.objects.filter(is_active=True).prefetch_related(
        "spots", "modes"
    )
    serializer_class = CourseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        # create() 側で owner を取れるように request を渡す
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
