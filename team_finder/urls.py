from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Подключаем проекты и пользователей с префиксами
    path('projects/', include('projects.urls', namespace='projects')),
    path('users/', include('users.urls', namespace='users')),
    # Добавляем пустой путь для главной страницы (редирект на список проектов)
    path('', include('projects.urls', namespace='projects')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
