import re

# Ограничения длины полей моделей (строго по ТЗ Варианта 2)
MAX_PROJECT_NAME_LENGTH = 200
MAX_PROJECT_STATUS_LENGTH = 6
MAX_USER_NAME_LENGTH = 124
MAX_USER_SURNAME_LENGTH = 124
MAX_USER_PHONE_LENGTH = 12
MAX_USER_ABOUT_LENGTH = 256
MAX_SKILL_NAME_LENGTH = 124

# Статусы проекта для выпадающего списка
PROJECT_STATUS_CHOICES = [
    ('open', 'Open'),
    ('closed', 'Closed'),
]

# Настройки пагинации и лимитов
PROJECTS_PER_PAGE = 12
USERS_PER_PAGE = 12
SKILL_AUTOCOMPLETE_LIMIT = 10

# Регулярные выражения и домены для валидации
PHONE_REGEX = re.compile(r'^(8|\+7)\d{10}$')
GITHUB_DOMAIN = "github.com"

# Официальные тексты ошибок для Django-форм
ERROR_PHONE_FORMAT = "Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
ERROR_PHONE_DUPLICATE = "Пользователь с таким номером телефона уже зарегистрирован."
ERROR_GITHUB_LINK = "Ссылка должна вести именно на домен github.com"
ERROR_AUTH_FAILED = "Неверный имейл или пароль"
ERROR_PASSWORD_MISMATCH = "Новые пароли не совпадают."
ERROR_OLD_PASSWORD_WRONG = "Неверный старый пароль."

# Палитра приятных цветов для генерации автоматических аватарок (RGB)
AVATAR_BG_COLORS = [
    (100, 149, 237), (70, 130, 180), (46, 139, 87),
    (102, 205, 170), (176, 196, 222), (218, 165, 32),
    (188, 143, 143), (139, 115, 85), (205, 133, 63)
]
