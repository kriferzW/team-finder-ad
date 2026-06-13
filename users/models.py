from constants import (
    MAX_USER_NAME_LENGTH, MAX_USER_SURNAME_LENGTH,
    MAX_USER_PHONE_LENGTH, MAX_USER_ABOUT_LENGTH,
    MAX_SKILL_NAME_LENGTH, AVATAR_BG_COLORS
)
import random
import sys
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

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
    avatar = models.ImageField(
        upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватарка')
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
        # Если аватарка не загружена, генерируем её автоматически перед сохранением
        if not self.avatar:
            self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        """Автоматическая генерация аватарки на основе первой буквы Имени."""
        size = (200, 200)
        bg_color = random.choice(AVATAR_BG_COLORS)
        img = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(img)

        letter = self.name[0].upper() if self.name else "U"

        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except IOError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (size[0] - w) / 2
        y = (size[1] - h) / 2 - 10

        draw.text((x, y), letter, fill=(255, 255, 255), font=font)

        from io import BytesIO
        f = BytesIO()
        img.save(f, format='JPEG')
        self.avatar.save(f"{self.email}_avatar.jpg",
                         ContentFile(f.getvalue()), save=False)
