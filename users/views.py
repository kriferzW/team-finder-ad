from http import HTTPStatus

from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from constants import PROJECTS_PER_PAGE, SKILL_AUTOCOMPLETE_LIMIT, USERS_PER_PAGE
from team_finder.utils import get_paginated_page
from users.forms import UserLoginForm, UserProfileForm, UserRegisterForm
from users.models import Skill

User = get_user_model()


def _save_user_skills(user, skills_str):
    if skills_str is not None:
        skill_names = [name.strip() for name in skills_str.split(",") if name.strip()]
        skills = []
        for name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills.append(skill)
        user.skills.set(skills)


def user_list(request):
    """Страница со всеми зарегистрированными пользователями (Вариант 2)."""
    # ТЗ: "отсортировав в порядке добавления в базу (по id)"
    queryset = User.objects.prefetch_related("skills").order_by("id")

    # ТЗ Вариант 2: фильтрация участников по навыкам
    active_skill = request.GET.get("skill")
    if active_skill:
        queryset = queryset.filter(skills__name=active_skill)

    # ТЗ Вариант 2: "all_skills": <все добавленные в БД навыки>
    all_skills = Skill.objects.all().order_by("name")

    # Базовая функциональность: пагинация по 12 профилей
    participants_page = get_paginated_page(request, queryset, USERS_PER_PAGE)

    query_prefix = f"skill={active_skill}&" if active_skill else ""

    context = {
        "participants": participants_page,
        "page_obj": participants_page,
        "all_skills": all_skills,
        "active_skill": active_skill,
        "query_prefix": query_prefix,
    }
    return render(request, "users/participants.html", context)


def user_profile(request, pk):
    """Публичный профиль участника (Вариант 2)."""
    user_instance = get_object_or_404(User, pk=pk)
    # Передаем как user, чтобы шаблон корректно отображал данные просматриваемого профиля
    return render(request, "users/user-details.html", {"user": user_instance})


@login_required
def profile_edit(request):
    """Форма редактирования профиля пользователя по макету Варианта 2."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            if "skills" in form.cleaned_data:
                _save_user_skills(user, form.cleaned_data["skills"])
            return redirect("users:user_profile", pk=request.user.pk)
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


def user_login(request):
    """Страница входа по Email и Паролю."""
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("projects:project_list")
    else:
        form = UserLoginForm(request)
    return render(request, "users/login.html", {"form": form})


def user_register(request):
    """Страница регистрации."""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if "skills" in form.cleaned_data:
                _save_user_skills(user, form.cleaned_data["skills"])
            login(request, user)
            return redirect("projects:project_list")
    else:
        form = UserRegisterForm()

    # Передаем все навыки для автодополнения (datalist)
    all_skills = Skill.objects.all().order_by("name")
    return render(
        request, "users/register.html", {"form": form, "all_skills": all_skills}
    )


def user_logout(request):
    """Выход из аккаунта."""
    logout(request)
    return redirect("projects:project_list")


# =====================================================================
#  ЛОГИКА ДЛЯ ВАРИАНТА 2 (Управление навыками через JS/AJAX без перезагрузки)
# =====================================================================


def skill_autocomplete(request):
    """Автодополнение навыков (первые 10 штук в алфавитном порядке)."""
    query = request.GET.get("q", "")
    # Используем возможности ORM для фильтрации на уровне SQL (QuerySet)
    skills = Skill.objects.filter(name__istartswith=query).order_by("name")[
        :SKILL_AUTOCOMPLETE_LIMIT
    ]
    data = list(skills.values("id", "name"))
    return JsonResponse(data, safe=False)


@login_required
def add_skill(request, pk):
    """Добавление навыка в профиль (Вариант 2)."""
    if request.user.pk != pk:
        return JsonResponse({"error": "Permission denied"}, status=HTTPStatus.FORBIDDEN)

    user_instance = User.objects.filter(pk=pk).first()
    if not user_instance:
        return JsonResponse({"error": "User not found"}, status=HTTPStatus.NOT_FOUND)

    skill_id = None
    name = None

    # Поддерживаем JSON-запросы от skills.js
    if request.content_type == "application/json":
        import json

        try:
            body = json.loads(request.body)
            skill_id = body.get("skill_id")
            name = body.get("name")
        except json.JSONDecodeError:
            pass

    # Резервный вариант для URL-encoded/POST
    if not skill_id and not name:
        skill_id = request.POST.get("skill_id")
        name = request.POST.get("name")

    created = False
    added = False
    skill = None

    if skill_id:
        skill = Skill.objects.filter(id=skill_id).first()
        if not skill:
            return JsonResponse(
                {"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND
            )
    elif name:
        skill, created = Skill.objects.get_or_create(name=name.strip())

    if skill:
        has_skill = user_instance.skills.filter(id=skill.id).exists()
        if not has_skill:
            user_instance.skills.add(skill)
            added = True

    # Возвращаем расширенную информацию (для соответствия ТЗ и совместимости с JS)
    return JsonResponse(
        {
            "skill_id": skill.id if skill else None,
            "id": skill.id if skill else None,
            "name": skill.name if skill else "",
            "created": created,
            "added": added,
        }
    )


@login_required
def remove_skill(request, pk, skill_id):
    """Удаление навыка из профиля (Вариант 2)."""
    if request.user.pk != pk:
        return JsonResponse({"error": "Permission denied"}, status=HTTPStatus.FORBIDDEN)

    user_instance = User.objects.filter(pk=pk).first()
    if not user_instance:
        return JsonResponse({"error": "User not found"}, status=HTTPStatus.NOT_FOUND)

    skill = Skill.objects.filter(id=skill_id).first()
    if not skill:
        return JsonResponse({"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND)

    has_skill = user_instance.skills.filter(id=skill.id).exists()
    if has_skill:
        user_instance.skills.remove(skill)
        return JsonResponse({"status": "ok"})

    return JsonResponse(
        {"error": "Skill not found in profile"}, status=HTTPStatus.BAD_REQUEST
    )


@login_required
def password_change(request):
    """Форма изменения пароля пользователя (по ТЗ)."""
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:user_profile", pk=user.pk)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "users/change_password.html", {"form": form})
