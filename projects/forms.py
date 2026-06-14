from django import forms
from django.core.exceptions import ValidationError

from constants import ERROR_GITHUB_LINK, GITHUB_DOMAIN
from projects.models import Project


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта TeamFinder."""

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название проекта",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Опишите суть проекта и кого вы ищете",
                }
            ),
            "github_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/your-project",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and GITHUB_DOMAIN not in url:
            raise ValidationError(ERROR_GITHUB_LINK)
        return url
