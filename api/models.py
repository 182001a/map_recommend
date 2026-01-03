from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class CourseTemplate(models.Model):
    """AIが提案した、またはユーザーが保存した『散歩コースの設計図』"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_templates')
    title = models.CharField(max_length=255, verbose_name="コース名")
    description = models.TextField(blank=True, verbose_name="説明")
    
    # AI/検索用のメタデータ
    ai_context = models.JSONField(default=dict, blank=True, help_text="生成時の気分や条件（プロンプト等）")
    tags = models.JSONField(default=list, blank=True, help_text="['公園', '静か'] などのタグ")
    
    generated_by_ai = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True, verbose_name="公開設定")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CourseSpotTemplate(models.Model):
    """コースレシピに含まれる立ち寄り予定地点"""
    course_template = models.ForeignKey(CourseTemplate, on_delete=models.CASCADE, related_name='spots')
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    order_index = models.PositiveIntegerField(default=0, verbose_name="巡回順序")
    estimated_stay_min = models.PositiveIntegerField(default=0, verbose_name="滞在予定時間(分)")

    class Meta:
        ordering = ['order_index']


# 2. 散歩の実績（実際のログ）
class WalkSession(models.Model):
    """実際に歩いた記録"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='walk_sessions')
    course_template = models.ForeignKey(CourseTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=255, default="新しい散歩")
    
    # 【最重要】軌跡データ。[[lat, lng, timestamp], ...] の形式で保存
    trajectory = models.JSONField(default=list, verbose_name="移動経路データ")
    
    total_distance_m = models.FloatField(default=0.0, verbose_name="総移動距離(m)")
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class WalkSpotVisit(models.Model):
    """散歩中に実際に立ち寄った場所"""
    walk_session = models.ForeignKey(WalkSession, on_delete=models.CASCADE, related_name='visits')
    place_name = models.CharField(max_length=255, verbose_name="場所名")
    place_id = models.CharField(max_length=255, blank=True, help_text="Google/MapboxのPlaceID")
    lat = models.FloatField()
    lng = models.FloatField()
    arrival_at = models.DateTimeField(null=True, blank=True)
    stay_duration_sec = models.PositiveIntegerField(default=0)

class WalkPhoto(models.Model):
    """散歩中に撮影した写真"""
    walk_session = models.ForeignKey(WalkSession, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='walk_photos/')
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    taken_at = models.DateTimeField(auto_now_add=True)


# 3. SNS・安全機能
class UserPrivacyMask(models.Model):
    """自宅周辺などを隠すための設定"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='privacy_masks')
    center_lat = models.FloatField()
    center_lng = models.FloatField()
    radius_m = models.PositiveIntegerField(default=200, help_text="半径(メートル)")