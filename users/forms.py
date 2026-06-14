from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from constants import (
    ERROR_GITHUB_LINK,
    ERROR_PHONE_DUPLICATE,
    ERROR_PHONE_FORMAT,
    GITHUB_DOMAIN,
    PHONE_REGEX,
)
from team_finder.utils import validate_phone_number
from users.models import Skill, User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя по ТЗ."""

    name = forms.CharField(
        label="Имя", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    surname = forms.CharField(
        label="Фамилия", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+7XXXXXXXXXX"}
        ),
    )

    skills = forms.CharField(
        label="Навыки (через запятую)",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Python, Django, HTML, CSS"}
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "name", "surname", "phone")

    def save(self, commit=True):
        return super().save(commit=commit)

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        return validate_phone_number(phone, User)


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля: аватар в виде текстовой ссылки, навыки убраны."""

    name = forms.CharField(
        label="Имя", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    surname = forms.CharField(
        label="Фамилия", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    # ИСПРАВЛЕНО: Теперь это просто текстовое поле для ввода URL-ссылки на фото
    avatar = forms.URLField(
        label="Ссылка на аватар",
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "https://example.com/photo.jpg",
            }
        ),
    )

    skills = forms.CharField(
        label="Навыки (через запятую)",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Python, Django, HTML, CSS"}
        ),
    )

    about = forms.CharField(
        label="О себе",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    phone = forms.CharField(
        label="Телефон", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    github_url = forms.URLField(
        label="GitHub",
        required=False,
        widget=forms.URLInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        # ИСПРАВЛЕНО: Убрали 'skills' из полей формы (поскольку управляем им вручную через CharField)
        fields = ("name", "surname", "email", "avatar", "about", "phone", "github_url")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Инициализируем поле навыков строкой с запятыми
            self.fields["skills"].initial = ", ".join(
                self.instance.skills.values_list("name", flat=True)
            )

    def save(self, commit=True):
        return super().save(commit=commit)

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        current_user_id = self.instance.pk if self.instance else None
        return validate_phone_number(phone, User, current_user_id)

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and GITHUB_DOMAIN not in url:
            raise ValidationError(ERROR_GITHUB_LINK)
        return url


class UserLoginForm(AuthenticationForm):
    """Форма авторизации."""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    @property
    def email(self):
        return self["username"]
