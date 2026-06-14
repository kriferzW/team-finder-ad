from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Skill, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Как будут отображаться колонки в списке пользователей
    list_display = ("email", "name", "surname", "phone", "is_staff", "is_active")

    # По каким полям будет работать поиск вверху страницы
    search_fields = ("email", "name", "surname", "phone")

    # Фильтры в правой панели
    list_filter = ("is_staff", "is_active", "skills")

    # Сортировка по умолчанию
    ordering = ("email",)

    # Настройка отображения полей при редактировании пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональная информация",
            {"fields": ("name", "surname", "phone", "avatar", "about", "github_url")},
        ),
        ("Навыки (Вариант 2)", {"fields": ("skills",)}),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    # Поля, которые нужно заполнять при создании пользователя через админку
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "surname", "phone", "password"),
            },
        ),
    )
    filter_horizontal = ("skills", "groups", "user_permissions")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
