from projects.models import Project
from constants import GITHUB_DOMAIN, ERROR_GITHUB_LINK
import sys
import os
from django import forms
from django.core.exceptions import ValidationError

# Гарантируем, что корень проекта находится в путях поиска Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта TeamFinder."""
    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название проекта'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите суть проекта и кого вы ищете'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/your-project'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and GITHUB_DOMAIN not in url:
            raise ValidationError(ERROR_GITHUB_LINK)
        return url
