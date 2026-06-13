from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('list', views.user_list, name='user_list'),
    path('<int:pk>/', views.user_profile, name='user_profile'),
    path('edit-profile/', views.profile_edit, name='edit_profile'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('change-password/', views.password_change, name='password_change'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # ТЗ пути (Вариант 2)
    path('skills/', views.skill_autocomplete, name='skill_autocomplete'),
    path('<int:pk>/skills/add/', views.add_skill, name='add_skill'),
    path('<int:pk>/skills/<int:skill_id>/remove/', views.remove_skill, name='remove_skill'),

    # Совместимость с inline-скриптами
    path('skill-autocomplete/', views.skill_autocomplete, name='skill_autocomplete_compat'),
    path('<int:pk>/add-skill/', views.add_skill, name='add_skill_compat'),
    path('<int:pk>/remove-skill/<int:skill_id>/', views.remove_skill, name='remove_skill_compat'),
]
