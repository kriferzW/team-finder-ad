from projects.forms import ProjectForm
from projects.models import Project
from constants import PROJECTS_PER_PAGE
import sys
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Гарантируем правильные пути импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def project_list(request):
    """Главная страница: список всех открытых проектов с пагинацией."""
    # Фильтруем только открытые проекты и сортируем (новые вверху)
    projects_queryset = Project.objects.filter(
        status='open').select_related('owner')

    # Подключаем пагинацию из констант
    paginator = Paginator(projects_queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, pk):
    """Страница отдельного проекта."""
    project = get_object_or_404(Project, pk=pk)
    context = {
        'project': project,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create(request):
    """Создание нового проекта (доступно только авторизованным)."""
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user  # Автоматически назначаем текущего юзера автором
        project.save()
        form.save_m2m()  # Нужно для сохранения связей, если появятся many-to-many
        return redirect('projects:project_list')

    return render(request, 'projects/project_form.html', {'form': form, 'is_edit': False})


@login_required
def project_edit(request, pk):
    """Редактирование проекта его автором."""
    project = get_object_or_404(Project, pk=pk)

    # Проверяем, что редактирует именно хозяин проекта
    if project.owner != request.user:
        return redirect('projects:project_detail', pk=pk)

    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('projects:project_detail', pk=pk)

    return render(request, 'projects/project_form.html', {'form': form, 'project': project, 'is_edit': True})
