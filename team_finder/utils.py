from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.templatetags.static import static

from constants import ERROR_PHONE_DUPLICATE, ERROR_PHONE_FORMAT, PHONE_REGEX


def get_paginated_page(request, queryset, per_page):
    """
    Пагинация для QuerySet.
    Возвращает объект страницы (Page).
    """
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def validate_phone_number(phone, user_model, current_user_id=None):
    """
    Валидация номера телефона.
    Проверяет формат по регулярному выражению и уникальность в БД.
    """
    if not PHONE_REGEX.match(phone):
        raise ValidationError(ERROR_PHONE_FORMAT)

    qs = user_model.objects.filter(phone=phone)
    if current_user_id:
        qs = qs.exclude(pk=current_user_id)

    if qs.exists():
        raise ValidationError(ERROR_PHONE_DUPLICATE)

    return phone


def get_user_avatar_url(avatar):
    """
    Возвращает корректный URL для аватарки: внешнюю ссылку или локальный путь media.
    """
    if not avatar:
        return static("images/default-avatar.png")
    if avatar.startswith(("http://", "https://")):
        return avatar

    media_url = settings.MEDIA_URL
    if not media_url.startswith("/"):
        media_url = "/" + media_url

    avatar_path = avatar
    if avatar_path.startswith("media/"):
        avatar_path = avatar_path[len("media/") :]
    elif avatar_path.startswith("/media/"):
        avatar_path = avatar_path[len("/media/") :]

    return f"{media_url}{avatar_path}"
