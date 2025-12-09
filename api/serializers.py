from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import (
    CustomUser,
    CourseTemplate,
    CourseSpotTemplate,
    CourseMode,
    WalkSession,
    WalkSpotVisit,
    WalkPhoto,
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


class CourseModeSerializer(serializers.ModelSerializer):
    """モード一覧表示用（散歩 / 食事 / 観光など）"""

    class Meta:
        model = CourseMode
        fields = ["id", "code", "label"]


class CourseSpotTemplateSerializer(serializers.ModelSerializer):
    """コース内スポット（ひな型）"""

    class Meta:
        model = CourseSpotTemplate
        fields = [
            "id",
            "order",
            "name",
            "place_id",
            "category",
            "stay_time_min",
            "lat",
            "lng",
        ]


class CourseTemplateSerializer(serializers.ModelSerializer):
    """
    コースひな型シリアライザ。
    - 読み込み時: modes（code+label）と spots をネストで返す
    - 書き込み時: mode_codes（["walk", "meal"] など）＋ spots を受け取る
    """

    spots = CourseSpotTemplateSerializer(many=True)
    modes = CourseModeSerializer(many=True, read_only=True)
    mode_codes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="モードの code のリスト。例: ['walk', 'meal']",
    )

    class Meta:
        model = CourseTemplate
        fields = [
            "id",
            "title",
            "description",
            "mood",
            "default_distance_m",
            "default_duration_min",
            "modes",       # 読み取り専用
            "mode_codes",  # 書き込み専用
            "is_active",
            "spots",
        ]
        read_only_fields = ["id", "is_active", "modes"]

    def validate_mode_codes(self, value):
        if not value:
            return value
        codes = list(set(value))
        modes = CourseMode.objects.filter(code__in=codes)
        if modes.count() != len(codes):
            existing = set(m.code for m in modes)
            missing = [c for c in codes if c not in existing]
            raise serializers.ValidationError(
                f"存在しない mode code が含まれています: {missing}"
            )
        return value

    def create(self, validated_data):
        spots_data = validated_data.pop("spots", [])
        mode_codes = validated_data.pop("mode_codes", [])

        request = self.context.get("request")
        owner = None
        if request and request.user and request.user.is_authenticated:
            owner = request.user

        course = CourseTemplate.objects.create(owner=owner, **validated_data)

        # モード紐づけ
        if mode_codes:
            modes = list(CourseMode.objects.filter(code__in=set(mode_codes)))
            course.modes.set(modes)

        # スポット作成
        for spot in spots_data:
            CourseSpotTemplate.objects.create(course=course, **spot)

        return course

class WalkPhotoSerializer(serializers.ModelSerializer):
    """写真ログ"""

    class Meta:
        model = WalkPhoto
        fields = [
            "id",
            "session",
            "spot_visit",
            "image",
            "taken_at",
            "lat",
            "lng",
            "caption",
            "created_at",
        ]
        read_only_fields = ["id", "session", "created_at"]


class WalkSpotVisitSerializer(serializers.ModelSerializer):
    """スポット滞在ログ"""

    class Meta:
        model = WalkSpotVisit
        fields = [
            "id",
            "session",
            "course_spot_template",
            "name",
            "place_id",
            "lat",
            "lng",
            "arrived_at",
            "left_at",
            "stay_duration_sec",
            "created_at",
        ]
        read_only_fields = ["id", "session", "created_at"]


class WalkSessionSerializer(serializers.ModelSerializer):
    """散歩セッション本体"""

    # 今はネストをシンプルにしたいので、詳細は別エンドポイントで取る想定
    class Meta:
        model = WalkSession
        fields = [
            "id",
            "user",
            "course_template",
            "started_at",
            "ended_at",
            "total_distance_m",
            "total_duration_sec",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        if user is None or user.is_anonymous:
            raise serializers.ValidationError("ログインユーザーが必要です。")
        validated_data["user"] = user
        return super().create(validated_data)
