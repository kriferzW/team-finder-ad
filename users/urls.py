from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('list', views.user_list, name='user_list'),  # /users/list
    path('<int:pk>/', views.user_profile, name='user_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('change-password/', views.password_change, name='password_change'),
]
