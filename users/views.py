from users.forms import UserRegisterForm, UserLoginForm, UserProfileForm
from users.models import User
from constants import USERS_PER_PAGE
import sys
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Гарантируем правильные пути импорта констант
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def user_register(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('projects:project_list')

    form = UserRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        # Сразу логиним пользователя после успешной регистрации
        login(request, user)
        return redirect('projects:project_list')

    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """Авторизация пользователя (вход по email)."""
    if request.user.is_authenticated:
        return redirect('projects:project_list')

    form = UserLoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('projects:project_list')

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """Выход из аккаунта."""
    logout(request)
    return redirect('projects:project_list')


def user_profile(request, pk):
    """Просмотр чужого или своего профиля (Вариант 2 с выводом навыков)."""
    profile_user = get_object_or_404(
        User.objects.prefetch_related('skills'), pk=pk)

    # Получаем проекты, в которых этот пользователь является автором
    user_projects = profile_user.owned_projects.all()

    context = {
        'profile_user': profile_user,
        'user_projects': user_projects,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование собственного профиля."""
    form = UserProfileForm(request.POST or None,
                           request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('users:user_profile', pk=request.user.pk)

    return render(request, 'users/profile_edit.html', {'form': form})


def user_list(request):
    """Список всех пользователей с пагинацией."""
    users = User.objects.all()
    paginator = Paginator(users, USERS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'users/user_list.html', context)
