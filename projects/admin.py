from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Колонки в таблице проектов
    list_display = ("name", "owner", "status", "created_at")

    # Поля, по которым можно искать (ищет по названию проекта, а также по email автора)
    search_fields = ("name", "owner__email", "owner__name")

    # Фильтрация по статусу и дате создания
    list_filter = ("status", "created_at")

    # Возможность быстро поменять статус проекта прямо из списка, не заходя внутрь
    list_editable = ("status",)

    # Горизонтальный интерфейс для выбора участников команды
    filter_horizontal = ("participants",)
