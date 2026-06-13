import random
import sys
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from constants import (
    MAX_USER_NAME_LENGTH, MAX_USER_SURNAME_LENGTH,
    MAX_USER_PHONE_LENGTH, MAX_USER_ABOUT_LENGTH,
    MAX_SKILL_NAME_LENGTH, AVATAR_BG_COLORS
)

# Гарантируем, что корень проекта находится в путях поиска Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class UserManager(BaseUserManager):
    """Менеджер для управления кастомной моделью пользователя."""

    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email является обязательным полем')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name,
                          surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class Skill(models.Model):
    """Модель навыков (Специфика Варианта 2)."""
    name = models.CharField(
        max_length=MAX_SKILL_NAME_LENGTH,
        unique=True,
        verbose_name='Название навыка'
    )

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя для TeamFinder с авторизацией по Email."""
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    name = models.CharField(
        max_length=MAX_USER_NAME_LENGTH, verbose_name='Имя')
    surname = models.CharField(
        max_length=MAX_USER_SURNAME_LENGTH, verbose_name='Фамилия')
    phone = models.CharField(
        max_length=MAX_USER_PHONE_LENGTH, unique=True, verbose_name='Номер телефона')

    # ИСПРАВЛЕНО: Изменили на URLField и увеличили длину до 500
    avatar = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ссылка на аватарку'
    )

    about = models.TextField(
        max_length=MAX_USER_ABOUT_LENGTH, blank=True, verbose_name='О себе')
    github_url = models.URLField(blank=True, verbose_name='Ссылка на GitHub')

    # Связь многие-ко-многим с навыками
    skills = models.ManyToManyField(
        Skill,
        related_name='users',
        blank=True,
        verbose_name='Навыки'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"

    def save(self, *args, **kwargs):
        # Если ссылка на аватарку не заполнена, генерируем ссылку на красивую заглушку
        if not self.avatar:
            self.generate_default_avatar_url()
        super().save(*args, **kwargs)

    @property
    def avatar_url(self):
        """Возвращает корректный URL для аватарки: внешнюю ссылку или локальный путь media."""
        if not self.avatar:
            from django.templatetags.static import static
            return static('images/default-avatar.png')
        if self.avatar.startswith(('http://', 'https://')):
            return self.avatar
        
        # Если это относительный путь (например, из старой ImageField базы), добавляем /media/
        from django.conf import settings
        media_url = settings.MEDIA_URL
        if not media_url.startswith('/'):
            media_url = '/' + media_url
            
        avatar_path = self.avatar
        if avatar_path.startswith('media/'):
            avatar_path = avatar_path[len('media/'):]
        elif avatar_path.startswith('/media/'):
            avatar_path = avatar_path[len('/media/'):]
            
        return f"{media_url}{avatar_path}"

    def generate_default_avatar_url(self):
        """Формирует ссылку на UI-Avatars на основе первой буквы имени."""
        letter = self.name[0].upper() if self.name else "U"

        # Берем случайный цвет из твоего списка AVATAR_BG_COLORS в constants.py
        # Если цвета там в HEX (например '333333'), то этот сервис их отлично съест.
        # Если там RGB-кортежи, то для простоты можно захардкодить красивый цвет, например '7000ff'
        bg_color = random.choice(
            AVATAR_BG_COLORS) if AVATAR_BG_COLORS else '7000ff'

        # Если в константах HEX-строка идет с решеткой (#f4f4f4), убираем её для URL API
        if isinstance(bg_color, str):
            bg_color = bg_color.lstrip('#')
        else:
            # Если вдруг в константах были RGB-кортежи типа (112, 0, 255)
            bg_color = '7000ff'

        # Используем бесплатный и стабильный сервис генерации аватарок по буквам
        self.avatar = f"https://ui-avatars.com/api/?name={letter}&background={bg_color}&color=fff&size=200"
