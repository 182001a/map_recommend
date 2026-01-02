from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import (
    CustomUser,
)


class UserSerializer(serializers.ModelSerializer):
    """閲覧用ユーザー情報"""

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    """登録用ユーザーシリアライザ"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user