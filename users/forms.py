from users.models import User, Skill
from constants import PHONE_REGEX, GITHUB_DOMAIN, ERROR_PHONE_FORMAT, ERROR_GITHUB_LINK
import sys
import os
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

# Гарантируем, что корень проекта находится в путях поиска Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя (Вариант 2)."""
    name = forms.CharField(label="Имя", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    surname = forms.CharField(label="Фамилия", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    phone = forms.CharField(label="Номер телефона", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+7XXXXXXXXXX'}))

    # Поле выбора навыков (ManyToManyField в форме)
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        label="Навыки",
        # select2 пригодится для красивого интерфейса
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "name", "surname", "phone", "skills")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not PHONE_REGEX.match(phone):
            raise ValidationError(ERROR_PHONE_FORMAT)
        return phone


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя."""
    class Meta:
        model = User
        fields = ("name", "surname", "phone", "avatar",
                  "about", "github_url", "skills")
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'skills': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not PHONE_REGEX.match(phone):
            raise ValidationError(ERROR_PHONE_FORMAT)
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and GITHUB_DOMAIN not in url:
            raise ValidationError(ERROR_GITHUB_LINK)
        return url


class UserLoginForm(AuthenticationForm):
    """Форма авторизации (заменяет username на email)."""
    username = forms.EmailField(label="Email", widget=forms.EmailInput(
        attrs={'class': 'form-control', 'autofocus': True}))
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
