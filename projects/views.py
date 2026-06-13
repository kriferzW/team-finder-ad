from django.http import JsonResponse
from projects.forms import ProjectForm
from projects.models import Project
from constants import PROJECTS_PER_PAGE
import os
import sys
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Гарантируем правильные пути импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ИСПРАВЛЕНО: Явно импортируем константу PROJECTS_PER_PAGE из твоего файла constants.py


def project_list(request):
    """Главная страница: список всех проектов, отсортированных от новых к старым."""
    # Получаем все проекты из базы данных
    projects_queryset = Project.objects.all().order_by(
        '-created_at').select_related('owner')

    # Теперь PROJECTS_PER_PAGE определён, и пагинатор отработает без NameError
    paginator = Paginator(projects_queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Передаём обе переменные, чтобы фронтенд точно зацепил данные
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, pk):
    """Страница подробной информации о конкретном проекте."""
    project = get_object_or_404(Project, pk=pk)
    context = {
        'project': project,
    }
    return render(request, 'projects/project-details.html', context)


@login_required
def project_create(request):
    """Создание нового проекта."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  # Привязываем текущего авторизованного пользователя
            project.save()
            # Добавляем создателя в команду проекта
            project.participants.add(request.user)
            form.save_m2m()
            return redirect(f'/projects/{project.pk}/')
    else:
        form = ProjectForm()

    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def project_edit(request, pk):
    """Редактирование проекта его автором."""
    project = get_object_or_404(Project, pk=pk)

    # Защита: редактировать проект может только его владелец
    if project.owner != request.user:
        return redirect(f'/projects/{project.pk}/')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project.pk}/')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def project_complete(request, pk):
    """Изменение статуса проекта на closed (по ТЗ)."""
    project = get_object_or_404(Project, pk=pk)
    if project.owner == request.user and project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"error": "Invalid project status or not owner"}, status=400)


@login_required
def project_toggle_participate(request, pk):
    """Добавление/удаление участника из проекта."""
    project = get_object_or_404(Project, pk=pk)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})
