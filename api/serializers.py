from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import (
    CustomUser,
    CourseTemplate,
    WalkSession,
    UserPrivacyMask,
    CourseSpotTemplate,
    WalkSpotVisit,
    WalkPhoto
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

class CourseSpotTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSpotTemplate
        fields = ['id', 'name', 'lat', 'lng', 'order_index', 'estimated_stay_min']

class CourseTemplateSerializer(serializers.ModelSerializer):
    spots = CourseSpotTemplateSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = CourseTemplate
        fields = ['id', 'user', 'title', 'description', 'ai_context', 'tags', 'generated_by_ai', 'is_public', 'spots']

# 3. 散歩実績（Session）関連
class WalkSpotVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalkSpotVisit
        fields = ['id', 'place_name', 'place_id', 'lat', 'lng', 'arrival_at', 'stay_duration_sec']

class WalkPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalkPhoto
        fields = ['id', 'image', 'lat', 'lng', 'taken_at']

class WalkSessionSerializer(serializers.ModelSerializer):
    visits = WalkSpotVisitSerializer(many=True, read_only=True)
    photos = WalkPhotoSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = WalkSession
        fields = [
            'id', 'user', 'course_template', 'title', 
            'trajectory', 'total_distance_m', 
            'start_at', 'end_at', 'is_public', 'visits', 'photos'
        ]

    # バリデーション例：軌跡データがリスト形式かチェック
    def validate_trajectory(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("軌跡データはリスト形式である必要があります。")
        return value

# 4. プライバシー設定
class UserPrivacyMaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPrivacyMask
        fields = ['id', 'center_lat', 'center_lng', 'radius_m']