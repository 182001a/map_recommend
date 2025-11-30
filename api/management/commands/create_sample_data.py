# api/management/commands/create_sample_data.py

from django.core.management.base import BaseCommand
from ...models import CourseTemplate, CourseSpotTemplate, CourseMode


class Command(BaseCommand):
    help = "SampleCourseView 相当のサンプルコースをDBに投入するコマンド"

    def handle(self, *args, **options):
        # まずモードを用意（散歩 / 食事 / 観光）
        walk_mode, _ = CourseMode.objects.get_or_create(
            code="walk",
            defaults={"label": "散歩"},
        )
        meal_mode, _ = CourseMode.objects.get_or_create(
            code="meal",
            defaults={"label": "食事"},
        )
        sightseeing_mode, _ = CourseMode.objects.get_or_create(
            code="sightseeing",
            defaults={"label": "観光"},
        )

        if CourseTemplate.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "CourseTemplate が既に存在しています。何もしません。"
                )
            )
            return

        # 1. リラックス散歩コース
        relax = CourseTemplate.objects.create(
            title="リラックス散歩コース",
            description="公園とカフェでゆっくり過ごすコース",
            mood=CourseTemplate.Mood.RELAX,
            default_distance_m=3200,
            default_duration_min=90,
            is_active=True,
        )
        relax.modes.add(walk_mode)

        CourseSpotTemplate.objects.create(
            course=relax,
            order=1,
            name="川沿い公園",
            place_id="dummy-1",
            category="park",
            stay_time_min=30,
            lat=35.0,
            lng=135.0,
        )
        CourseSpotTemplate.objects.create(
            course=relax,
            order=2,
            name="カフェA",
            place_id="dummy-2",
            category="cafe",
            stay_time_min=45,
            lat=35.001,
            lng=135.002,
        )

        # 2. グルメ巡りコース
        gourmet = CourseTemplate.objects.create(
            title="グルメ巡りコース",
            description="ラーメンとスイーツを楽しむコース",
            mood=CourseTemplate.Mood.HUNGRY,
            default_distance_m=2100,
            default_duration_min=80,
            is_active=True,
        )
        # 散歩＋食事の複数モード
        gourmet.modes.add(walk_mode, meal_mode)

        CourseSpotTemplate.objects.create(
            course=gourmet,
            order=1,
            name="ラーメン屋",
            place_id="dummy-3",
            category="ramen",
            stay_time_min=40,
            lat=35.002,
            lng=135.001,
        )
        CourseSpotTemplate.objects.create(
            course=gourmet,
            order=2,
            name="スイーツショップ",
            place_id="dummy-4",
            category="sweets",
            stay_time_min=40,
            lat=35.003,
            lng=135.003,
        )

        # 3. 観光スポット欲張りコース
        active = CourseTemplate.objects.create(
            title="観光スポット欲張りコース",
            description="神社と展望台を巡るアクティブコース",
            mood=CourseTemplate.Mood.ACTIVE,
            default_distance_m=5000,
            default_duration_min=120,
            is_active=True,
        )
        # 散歩＋観光
        active.modes.add(walk_mode, sightseeing_mode)

        CourseSpotTemplate.objects.create(
            course=active,
            order=1,
            name="神社",
            place_id="dummy-5",
            category="shrine",
            stay_time_min=30,
            lat=35.004,
            lng=135.004,
        )
        CourseSpotTemplate.objects.create(
            course=active,
            order=2,
            name="展望台",
            place_id="dummy-6",
            category="viewpoint",
            stay_time_min=45,
            lat=35.005,
            lng=135.006,
        )

        self.stdout.write(self.style.SUCCESS("サンプルコースを3件投入しました。"))
