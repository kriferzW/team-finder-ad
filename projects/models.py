from django.conf import settings
from django.db import models

from constants import (
    MAX_PROJECT_NAME_LENGTH,
    MAX_PROJECT_STATUS_LENGTH,
    PROJECT_STATUS_CHOICES,
)


class Project(models.Model):
    """Модель проекта TeamFinder."""

    name = models.CharField(
        max_length=MAX_PROJECT_NAME_LENGTH, verbose_name="Название проекта"
    )
    description = models.TextField(verbose_name="Описание проекта")
    github_url = models.URLField(blank=True, verbose_name="Ссылка на GitHub проекта")

    # Статус проекта: 'open' или 'closed'
    status = models.CharField(
        max_length=MAX_PROJECT_STATUS_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default="open",
        verbose_name="Статус проекта",
    )

    # Создатель проекта
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор проекта",
    )

    # Участники проекта (команда)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники проекта",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
