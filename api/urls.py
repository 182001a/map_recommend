from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    MeView,
    CourseTemplateListCreateView,
    WalkSessionListCreateView,
    WalkSessionFinishView,
    WalkSpotVisitCreateView,
    WalkPhotoCreateView,
)

urlpatterns = [
    # 認証（Token発行ベース）
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", MeView.as_view(), name="auth-me"),

    # コース提案サンプル
    path(
        "course-templates/",
        CourseTemplateListCreateView.as_view(),
        name="course-template-list-create",
    ),

    path("walk-sessions/", WalkSessionListCreateView.as_view(), name="walksession-list-create"),
    path("walk-sessions/<int:pk>/finish/", WalkSessionFinishView.as_view(), name="walksession-finish"),
    path(
        "walk-sessions/<int:session_id>/spot-visits/",
        WalkSpotVisitCreateView.as_view(),
        name="walkspotvisit-create",
    ),
    path(
        "walk-sessions/<int:session_id>/photos/",
        WalkPhotoCreateView.as_view(),
        name="walkphoto-create",
    ),
]
