from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView  # Импортируем редирект

urlpatterns = [
    path("admin/", admin.site.urls),
    # Редирект с корня на список проектов
    path("", RedirectView.as_view(url="/projects/list", permanent=True)),
    path("projects/", include("projects.urls", namespace="projects")),
    path("users/", include("users.urls", namespace="users")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
