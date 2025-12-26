# booking-system

Приложение для бронирования комнат в отеле

## Требования

- Для комнат должны быть поля: номер/название, стоимость за сутки, количество мест
- Пользователи должны уметь фильтровать и сортировать комнаты по цене, по количеству мест
- Пользователи должны уметь искать свободные комнаты в заданном временном интервале
- Пользователи должны уметь забронировать свободную комнату
- Суперюзер должен уметь добавлять/удалять/редактировать комнаты и редактировать записи о бронях через админ панель Django
- Брони могут быть отменены как самим юзером, так и суперюзером
- Пользователи должны уметь регистрироваться и авторизовываться (логиниться)
- Чтобы забронировать комнату пользователи должны быть авторизованными. Просматривать комнаты можно без логина. Авторизованные пользователи должны видеть свои брони
- Автотесты
- Аннотации типов
- Линтер
- Автоформатирование кода
- Документация к API
- Инструкция по запуску приложения

## Стек

- Django 6.0
- Django REST Framework 3.16
- PostgreSQL
- drf-spectacular (API документация)
- Black (автоформатирование)
- Flake8 (линтер)
- Mypy (проверка типов)

## Установка и запуск

### Подготовка окружения

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd booking-system
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv .venv
source .venv/bin/activate 
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Установите переменные окружения:**
```bash
cp .env.example .env
```

### Запуск локально

1. **Запустите PostgreSQL:**
- Убедитесь, что PostgreSQL запущен и доступен по адресу из `.env` файла
- Создайте базу данных: `createdb yourdbname` (или используйте `psql`/GUI)

2. **Выполните миграции:**
```bash
python manage.py migrate
```

3. **Создайте суперпользователя (администратора):**
```bash
python manage.py createsuperuser
```

4. **(Опционально) Заполните базу тестовыми данными:**
```bash
python manage.py populate_db
```

5. **Запустите development сервер:**
```bash
python manage.py runserver
```

Сервер будет доступен по адресу: `http://localhost:8000`

## Использование API

### Документация API

- **OpenAPI схема (JSON):** http://localhost:8000/api/schema/
- **Swagger UI (интерактивная документация):** http://localhost:8000/api/docs/

### Основные эндпоинты

#### Аутентификация

**Регистрация:**
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword123"
}
```

**Логин**
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}
```

#### Просмотр комнат (без авторизации)

**Список всех комнат:**
```bash
GET /api/rooms/
```

**Фильтрация по цене:**
```bash
GET /api/rooms/?min_price=50&max_price=150
```

**Фильтрация по количеству мест:**
```bash
GET /api/rooms/?min_capacity=2&max_capacity=4
```

**Сортировка по цене:**
```bash
GET /api/rooms/?ordering=price_per_night  
GET /api/rooms/?ordering=-price_per_night
```

**Сортировка по количеству мест:**
```bash
GET /api/rooms/?ordering=capacity
GET /api/rooms/?ordering=-capacity
```

**Поиск доступных комнат в период:**
```bash
GET /api/rooms/?start_date=2025-03-01&end_date=2025-03-05
```

#### Бронирование (требует авторизации)

**Создание бронирования:**
```bash
POST /api/bookings/
Authorization: Token <your-token>
Content-Type: application/json

{
  "room": 1,
  "start_date": "2025-03-01",
  "end_date": "2025-03-05"
}
```

**Список своих бронирований:**
```bash
GET /api/bookings/
Authorization: Token <your-token>
```

**Отмена бронирования:**
```bash
DELETE /api/bookings/<booking-id>/
Authorization: Token <your-token>
```

## Django Admin

Администратор может управлять комнатами и бронированиями через админ панель:

**URL:** http://localhost:8000/admin/

**Функции:**
- Добавление, редактирование и удаление комнат
- Просмотр и редактирование всех бронирований
- Фильтрация и поиск

## Тестирование

### Запуск тестов

```bash
python manage.py test booking -v 2
```

### Проверка качества кода

```bash
# Линтер (flake8)
flake8 booking/ emphasoft/

# Проверка типов (mypy)
mypy . --config-file=mypy.ini

# Проверка форматирования (black)
black . --check
```