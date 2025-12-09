from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser, FormParser

from .models import CourseTemplate, CourseMode, WalkSession, WalkSpotVisit, WalkPhoto
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CourseTemplateSerializer,
    CourseModeSerializer,
    WalkSessionSerializer,
    WalkSpotVisitSerializer,
    WalkPhotoSerializer,
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

class WalkSessionListCreateView(generics.ListCreateAPIView):
    """
    GET: 自分の散歩セッション一覧
    POST: 散歩開始（WalkSession 作成）
    """

    serializer_class = WalkSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WalkSession.objects.filter(user=self.request.user).order_by("-started_at")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
    
class WalkSessionFinishView(APIView):
    """
    POST /api/walk-sessions/<id>/finish/

    Body:
      {
        "ended_at": "...",
        "total_distance_m": 1234,
        "total_duration_sec": 3600
      }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            session = WalkSession.objects.get(pk=pk, user=request.user)
        except WalkSession.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = {
            "ended_at": request.data.get("ended_at"),
            "total_distance_m": request.data.get("total_distance_m"),
            "total_duration_sec": request.data.get("total_duration_sec"),
        }
        serializer = WalkSessionSerializer(
            session, data=data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class WalkSpotVisitCreateView(generics.CreateAPIView):
    """
    POST /api/walk-sessions/<session_id>/spot-visits/
    """

    serializer_class = WalkSpotVisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        session_id = self.kwargs["session_id"]
        try:
            session = WalkSession.objects.get(pk=session_id, user=self.request.user)
        except WalkSession.DoesNotExist:
            raise permissions.PermissionDenied("このセッションは存在しないか、あなたのものではありません。")

        serializer.save(session=session)

class WalkPhotoCreateView(generics.CreateAPIView):
    """
    POST /api/walk-sessions/<session_id>/photos/
    multipart/form-data で画像を送信
    """

    serializer_class = WalkPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        session_id = self.kwargs["session_id"]
        try:
            session = WalkSession.objects.get(pk=session_id, user=self.request.user)
        except WalkSession.DoesNotExist:
            raise permissions.PermissionDenied("このセッションは存在しないか、あなたのものではありません。")

        serializer.save(session=session)