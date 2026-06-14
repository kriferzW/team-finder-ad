from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list, name="project_list"),
    path("create-project/", views.project_create, name="project_create"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("<int:pk>/complete/", views.project_complete, name="project_complete"),
    path(
        "<int:pk>/toggle-participate/",
        views.project_toggle_participate,
        name="project_toggle_participate",
    ),
]
