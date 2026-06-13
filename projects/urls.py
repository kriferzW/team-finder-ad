from django.urls import path
from projects import views

app_name = 'projects'

urlpatterns = [
    # Путь для "/projects/list"
    path('list', views.project_list, name='project_list'),
    # Путь для "/projects/create-project"
    path('create-project', views.project_create, name='project_create'),
    # Остальные пути
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
]
