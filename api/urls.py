from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    MeView,
    CourseTemplateListCreateView,
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
]
