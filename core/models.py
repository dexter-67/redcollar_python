from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Point(models.Model):
    """
    Географическая точка на карте, созданная пользователем.
    """
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Название"),
        help_text=_("Опциональное название точки")
    )
    location = models.PointField(
        srid=4326,
        spatial_index=True,               # ← Вот здесь создаётся пространственный индекс
        verbose_name=_("Координаты"),
        help_text=_("Долгота и широта в WGS84 (EPSG:4326)")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_points',
        verbose_name=_("Создатель")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата изменения")
    )

    class Meta:
        verbose_name = _("Точка")
        verbose_name_plural = _("Точки")
        ordering = ["-created_at"]
        indexes = [
            # Обычный индекс по создателю — ускоряет фильтрацию "только мои точки"
            models.Index(fields=["created_by"], name="point_by_user_idx"),
        ]
        # Если хочешь уникальность названий внутри пользователя — раскомментируй
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["created_by", "name"],
        #         condition=models.Q(name__gt=""),
        #         name="unique_point_name_per_user"
        #     )
        # ]

    def __str__(self):
        name_part = self.name if self.name else f"ID {self.id}"
        return f"{name_part} ({self.location.y:.6f}, {self.location.x:.6f})"

    @property
    def latitude(self):
        """Для удобства в сериализаторах и API-ответах"""
        return self.location.y

    @property
    def longitude(self):
        """Для удобства в сериализаторах и API-ответах"""
        return self.location.x


class Message(models.Model):
    """
    Сообщение, привязанное к конкретной гео-точке.
    """
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_("Точка")
    )
    text = models.TextField(
        verbose_name=_("Текст сообщения")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_("Автор")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата изменения")
    )

    class Meta:
        verbose_name = _("Сообщение")
        verbose_name_plural = _("Сообщения")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["point"], name="msg_point_idx"),
            models.Index(fields=["created_by"], name="msg_by_user_idx"),
        ]

    def __str__(self):
        return f"Сообщение {self.id} от {self.created_by.username} к точке {self.point_id}"
