# Megano Store — Интернет-магазин

Дипломный проект — интернет-магазин на Django + REST API.

## Стек

- Python 3.12+
- Django 6.0
- Django REST Framework 3.17
- SQLite
- Vue 3 (CDN) + Axios (фронтенд)

## Установка и запуск

```bash
# Клонировать репозиторий
git clone <repo> && cd python_django_diploma

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Загрузить демо-данные
python manage.py load_demo_data

# Запустить сервер разработки
python manage.py runserver
```

Открыть `http://127.0.0.1:8000/`.

## Демо-пользователи

| Логин | Пароль | Имя |
|-------|--------|-----|
| ivan  | 123456 | Иван Петров |
| maria | 123456 | Мария Иванова |

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/sign-in` | Вход |
| POST | `/api/sign-up` | Регистрация |
| POST | `/api/sign-out` | Выход |
| GET | `/api/categories` | Категории |
| GET | `/api/catalog` | Каталог товаров |
| GET | `/api/products/popular` | Популярные товары |
| GET | `/api/products/limited` | Лимитированные товары |
| GET | `/api/product/<id>` | Детали товара |
| POST | `/api/product/<id>/review` | Отзыв на товар |
| GET | `/api/sales` | Акции |
| GET | `/api/banners` | Баннеры |
| GET/POST/DELETE | `/api/basket` | Корзина |
| GET/POST | `/api/orders` | Заказы |
| GET/POST | `/api/orders/<id>` | Детали заказа |
| POST | `/api/payment/<id>` | Оплата заказа |
| GET/POST | `/api/profile` | Профиль |
| POST | `/api/profile/password` | Смена пароля |
| POST | `/api/profile/avatar` | Загрузка аватара |
| GET | `/api/tags` | Теги |

## Структура проекта

```
python_django_diploma/
├── main/                 # Настройки Django-проекта
├── diploma-frontend/     # Frontend-приложение (интерфейс)
│   └── frontend/
│       ├── models.py     # Модели данных
│       ├── views_api.py  # API-эндпоинты
│       ├── serializers.py
│       ├── api_urls.py
│       └── management/   # Команды (load_demo_data)
├── static/               # Статика (CSS, JS, изображения)
├── media/                # Загружаемые файлы (изображения товаров)
├── manage.py
└── requirements.txt
```
