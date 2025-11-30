from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class CourseMode(models.Model):
    """
    コースの「モード」や目的。
    例: walk=散歩, meal=食事, sightseeing=観光 など。
    複数モードを1つのコースに紐づけられる。
    """

    code = models.CharField(
        max_length=30,
        unique=True,
        help_text="内部用コード。例: walk, meal, sightseeing など",
    )
    label = models.CharField(
        max_length=50,
        help_text="表示名。例: 散歩, 食事, 観光 など",
    )

    def __str__(self):
        return self.label


class CourseTemplate(models.Model):
    """
    コースの「ひな型」定義。
    SampleCourseView のデモコースや、将来ユーザーが作る共有コースの土台。
    """

    class Mood(models.TextChoices):
        RELAX = "relax", "リラックス"
        HUNGRY = "hungry", "グルメ"
        ACTIVE = "active", "アクティブ"

    # ★ タイトルは任意。未入力なら「日付_シーケンス番号」などを別ロジックで自動生成想定。
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text="任意。未設定の場合は日付_シーケンス番号などを自動付与する想定。",
    )
    description = models.TextField(blank=True)

    mood = models.CharField(
        max_length=20,
        choices=Mood.choices,
        default=Mood.RELAX,
    )

    # 内部表現はメートル / 分に統一
    default_distance_m = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="想定総距離（メートル）",
    )
    default_duration_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="想定所要時間（分）",
    )

    # ★ モード複数選択（散歩＋食事など）
    modes = models.ManyToManyField(
        CourseMode,
        related_name="courses",
        blank=True,
        help_text="散歩 / 食事 / 観光 など複数選択可",
    )

    is_active = models.BooleanField(default=True)

    owner = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_courses",
        help_text="システム提供コースなら null, ユーザー作成ならそのユーザー",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # タイトル未設定でも一応識別しやすいように
        return self.title or f"CourseTemplate#{self.id}"


class CourseSpotTemplate(models.Model):
    """
    コース内に並ぶスポット定義。
    1コースに対して1..Nレコード。
    """

    course = models.ForeignKey(
        CourseTemplate,
        on_delete=models.CASCADE,
        related_name="spots",
    )

    order = models.PositiveIntegerField(help_text="コース内の順番（1始まり）")

    name = models.CharField(max_length=100)
    place_id = models.CharField(
        max_length=100,
        help_text="Google Places API の place_id。長期保存はこのID中心に行う。",
    )

    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="cafe / park / shrine など任意のカテゴリ",
    )

    stay_time_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="想定滞在時間（分）。未設定ならデフォルト扱い。",
    )

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["course", "order"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.order}. {self.name} ({self.course_id})"
