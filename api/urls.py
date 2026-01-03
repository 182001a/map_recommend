from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseTemplateViewSet,
    WalkSessionViewSet,
    UserPrivacyMaskViewSet, 
    RegisterView,
    LoginView,
    MeView
)

router = DefaultRouter()
router.register(r'course-templates', CourseTemplateViewSet, basename='course-template')
router.register(r'walk-sessions', WalkSessionViewSet, basename='walk-session')
router.register(r'user-privacy-masks', UserPrivacyMaskViewSet, basename='user-privacy-mask')

urlpatterns = [
    # 認証（Token発行ベース）
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", MeView.as_view(), name="auth-me"),

    path('' , include(router.urls)),
]