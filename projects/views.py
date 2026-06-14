from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from constants import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN, PROJECTS_PER_PAGE
from projects.forms import ProjectForm
from projects.models import Project
from team_finder.utils import get_paginated_page


def project_list(request):
    """Главная страница: список всех проектов, отсортированных от новых к старым."""
    # Получаем все проекты из базы данных
    projects_queryset = (
        Project.objects.all().order_by("-created_at").select_related("owner")
    )

    page_obj = get_paginated_page(request, projects_queryset, PROJECTS_PER_PAGE)

    # Передаём обе переменные, чтобы фронтенд точно зацепил данные
    context = {
        "projects": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "projects/project_list.html", context)


def project_detail(request, pk):
    """Страница подробной информации о конкретном проекте."""
    project = get_object_or_404(Project, pk=pk)
    context = {
        "project": project,
    }
    return render(request, "projects/project-details.html", context)


@login_required
def project_create(request):
    """Создание нового проекта."""
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = (
                request.user
            )  # Привязываем текущего авторизованного пользователя
            project.save()
            # Добавляем создателя в команду проекта
            project.participants.add(request.user)
            form.save_m2m()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def project_edit(request, pk):
    """Редактирование проекта его автором."""
    project = get_object_or_404(Project, pk=pk)

    # Защита: редактировать проект может только его владелец
    if project.owner != request.user:
        return redirect("projects:project_detail", pk=project.pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@login_required
def project_complete(request, pk):
    """Изменение статуса проекта на closed (по ТЗ)."""
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return JsonResponse({"error": "Project not found"}, status=HTTPStatus.NOT_FOUND)

    if project.owner == request.user and project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})
    return JsonResponse(
        {"error": "Invalid project status or not owner"}, status=HTTPStatus.BAD_REQUEST
    )


@login_required
def project_toggle_participate(request, pk):
    """Добавление/удаление участника из проекта."""
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return JsonResponse({"error": "Project not found"}, status=HTTPStatus.NOT_FOUND)

    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not is_participant})
