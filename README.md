## TorJok — платформа адресной благотворительности

Единое пространство, где **нуждающиеся**, **частные благотворители** и **фонды** находят друг друга, обмениваются откликами и прозрачно фиксируют помощь.

Основная идея: уменьшить разрозненность благотворительной экосистемы, дать понятный интерфейс для запроса и предложения помощи и сделать каждое взаимодействие отслеживаемым.

---

##  Быстрый старт

### Запуск через Docker (рекомендуется)

```bash
# Клонирование репозитория
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>.git
cd torjok

# Запуск через Docker Compose
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

После запуска приложение будет доступно по адресу: `http://localhost:8080/`

Для остановки:
```bash
docker-compose down
```

### Запуск без Docker

```bash
# Клонирование репозитория
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>.git
cd torjok

# (рекомендуется) Создать и активировать виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux / macOS

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python main.py
```

После запуска приложение будет доступно по адресу: `http://127.0.0.1:8080/`

---

## Установка и настройка

### 1. Клонирование проекта
```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>.git
cd torjok
```

### 2. Виртуальное окружение (опционально, но желательно)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux / macOS
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка окружения
Создайте файл `.env` (по аналогии с `.env.example`, если добавите его) и задайте как минимум:

```bash
SECRET_KEY=ваш_секретный_ключ
```

По умолчанию путь к базе и шаблонам задаётся в `src/config.py`:
- `DATABASE = 'charity.db'`
- `TEMPLATE_FOLDER = 'templates'`

### 5. Инициализация БД и запуск
Инициализация БД выполняется автоматически при запуске `main.py`:

```bash
python main.py
```

---

## Использование

После запуска доступны три роли пользователей:

- **Нуждающийся (needy)**  
  - Создание запросов на помощь (с категорией, срочностью, городом)
  - Просмотр доступной помощи (предложения доноров и программы фондов)
  - Управление откликами на свои запросы

- **Благотворитель (donor)**  
  - Создание предложений помощи (тип, категория, сумма, город)
  - Просмотр запросов нуждающихся и отклик на них
  - Просмотр и поддержка программ фондов

- **Фонд (fund)**  
  - Создание программ помощи (категория, целевая сумма, город)
  - Управление пожертвованиями (pending / completed / rejected)
  - Работа с откликами от нуждающихся

> Скриншоты и GIF можно добавить позже в секцию `docs/` или прямо сюда.

---

## Конфигурация

### Переменные окружения

- `SECRET_KEY` — секретный ключ Flask (подпись сессий)

### Файлы конфигурации

- `src/config.py` — базовая конфигурация приложения:
  - `SECRET_KEY`
  - `DATABASE`
  - `TEMPLATE_FOLDER`
  - `DEBUG`
  - `HOST`
  - `PORT`

Для разных сред (dev/prod) можно добавить отдельные классы конфигурации и переключать их через переменную окружения.

---

## API и маршруты (высокий уровень)

Проект не предоставляет отдельного JSON API, основное взаимодействие идёт через HTML‑страницы и форму‑запросы. Ниже — ключевые маршруты:

- Аутентификация:
  - `GET /login`, `POST /login`
  - `GET /register`, `POST /register`
  - `GET /logout`
- Общие:
  - `GET /` — главная
  - `GET /dashboard/<user_type>` — личный кабинет по роли
- Нуждающиеся (`/needy/...`):
  - `GET, POST /needy/create-request`
  - `GET /needy/my-requests`
  - `GET /needy/available-help`
  - `POST /needy/respond-to-offer/<offer_id>/<offer_type>` (AJAX)
- Благотворители (`/donor/...`):
  - `GET, POST /donor/create-offer`
  - `GET /donor/my-offers`
  - `GET /donor/needy-requests`
  - `POST /donor/respond-to-request/<request_id>` (AJAX)
  - `GET /donor/fund-programs`
  - `POST /donor/donate-to-fund/<program_id>` (AJAX)
- Фонды (`/fund/...`):
  - `GET, POST /fund/create-program`
  - `GET /fund/my-programs`
  - `GET /fund/donations`
  - `POST /fund/confirm-donation/<donation_id>` (AJAX)
  - `POST /fund/reject-donation/<donation_id>` (AJAX)

Аутентификация основана на сессиях Flask, доступ к ролевым маршрутам ограничивается декораторами `@login_required` и `@user_type_required(...)`.

---

## Разработка

### Установка окружения для разработки
```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>.git
cd torjok
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Запуск в режиме разработки
```bash
python main.py  # DEBUG включён в src/config.py
```

### Тестирование
На данный момент отдельный тестовый набор не реализован. Рекомендуемый минимум:

- Ручное прохождение ключевых сценариев для трёх ролей
- Проверка работы форм (создание/отклики/пожертвования)
- Проверка ограничений доступа (нуждающийся не может зайти в `/donor/...` и т.п.)

При необходимости можно добавить:

- unit‑тесты для `src/utils.py` и `routes/auth.py`
- интеграционные тесты маршрутов с использованием `FlaskClient`

---

## Технологии

- **Backend**: Python 3, Flask
- **Database**: SQLite (через `sqlite3`)
- **Frontend**: HTML5, Bootstrap 5, Font Awesome 6, Vanilla JS (Fetch/AJAX)
- **Шаблоны**: Jinja2
- **Управление состоянием**: Flask sessions

---

## Структура проекта

```text
T/
├── main.py                  # Точка входа, фабрика Flask-приложения
├── requirements.txt         # Зависимости Python
├── Dockerfile              # Конфигурация Docker образа
├── docker-compose.yml      # Конфигурация Docker Compose
├── .dockerignore           # Исключения для Docker
├── charity.db              # Файл базы данных SQLite (создаётся автоматически)
│
├── src/                    # Исходный код приложения
│   ├── config.py           # Конфигурация приложения
│   ├── database.py         # Инициализация и доступ к БД
│   ├── utils.py            # Вспомогательные функции (хеширование паролей)
│   └── validators.py       # Валидаторы данных
│
├── routes/                 # Маршруты Flask (blueprints)
│   ├── __init__.py
│   ├── auth.py             # Авторизация и регистрация, декораторы
│   ├── main.py             # Главная страница и dashboard
│   ├── needy.py            # Маршруты для нуждающихся
│   ├── donor.py            # Маршруты для благотворителей
│   └── fund.py             # Маршруты для фондов
│
├── templates/              # HTML шаблоны (Jinja2)
│   ├── base.html           # Базовый шаблон
│   ├── home.html           # Главная страница
│   ├── auth/               # Страницы авторизации
│   │   ├── login.html
│   │   └── register.html
│   ├── main/               # Дашборды по ролям
│   │   ├── dashboard_donor.html
│   │   ├── dashboard_fund.html
│   │   └── dashboard_needy.html
│   ├── needy/              # Страницы для нуждающихся
│   │   ├── create_request.html
│   │   ├── my_requests.html
│   │   ├── available_help.html
│   │   └── responses.html
│   ├── donor/              # Страницы для благотворителей
│   │   ├── create_offer.html
│   │   ├── my_offers.html
│   │   ├── needy_requests.html
│   │   ├── fund_programs.html
│   │   └── responses.html
│   └── fund/               # Страницы для фондов
│       ├── create_program.html
│       ├── my_programs.html
│       ├── needy_requests.html
│       ├── donations.html
│       └── responses.html
│
└── static/                 # Статические файлы
    ├── img/                # Изображения (логотипы, иллюстрации)
    │   └── i.webp
    ├── js/                 # JavaScript файлы
    │   └── validation.js
    └── uploads/            # Загруженные пользователями файлы
```

---

## Docker

Проект полностью настроен для работы в Docker контейнерах.

### Требования

- Docker (версия 20.10 или выше)
- Docker Compose (версия 1.29 или выше)

### Быстрый запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>.git
   cd torjok
   ```

2. **Запустите контейнер:**
   ```bash
   docker-compose up --build
   ```

3. **Откройте браузер:**
   Приложение будет доступно по адресу: `http://localhost:8080/`

### Управление контейнером

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка контейнера
docker-compose down

# Пересборка образа
docker-compose build --no-cache

# Остановка и удаление контейнера с данными
docker-compose down -v
```

### Переменные окружения

Вы можете настроить приложение через переменные окружения в `docker-compose.yml`:

```yaml
environment:
  - SECRET_KEY=ваш-секретный-ключ
  - FLASK_ENV=production
```

Или создать файл `.env` в корне проекта:

```env
SECRET_KEY=ваш-секретный-ключ
FLASK_ENV=production
```

И обновить `docker-compose.yml`:

```yaml
env_file:
  - .env
```

### Структура Docker

- **Dockerfile** — описывает образ приложения
- **docker-compose.yml** — оркестрация контейнеров
- **.dockerignore** — исключает ненужные файлы из образа

### Важные замечания

- База данных `charity.db` монтируется как volume, поэтому данные сохраняются между перезапусками
- Директория `static/uploads` также монтируется для сохранения загруженных файлов
- При первом запуске база данных будет создана автоматически

### Запуск только через Dockerfile (без docker-compose)

```bash
# Сборка образа
docker build -t charity-app .

# Запуск контейнера
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/charity.db:/app/charity.db \
  -v $(pwd)/static/uploads:/app/static/uploads \
  -e SECRET_KEY=ваш-секретный-ключ \
  --name charity-app \
  charity-app
```

---

## Деплой (общие рекомендации)

- Использовать **виртуальное окружение** и отдельный конфигурационный файл для продакшена
- Вынести `SECRET_KEY` и параметры БД в переменные окружения
- Для продакшена:
  - Запуск через WSGI‑сервер (gunicorn/uWSGI) за nginx
  - Перенос с SQLite на PostgreSQL при росте нагрузки
- Возможный PaaS: Railway, Render, Heroku‑подобные сервисы (Flask + Gunicorn)

---

## Лицензия

Лицензия пока **не выбрана**. При публикации проекта в открытый доступ рекомендуется добавить секцию с выбранной лицензией (например, MIT) и отдельный файл `LICENSE`.

---

## Contributing

Пока проект находится в активной разработке небольшой командой. Базовый процесс участия:

1. Форк репозитория
2. Создание фиче‑ветки (`feature/...`)
3. Описание изменений в PR (что было сделано, какие маршруты/шаблоны затронуты)
4. Минимальное ручное тестирование перед PR

Ошибки и предложения можно описывать в разделе Issues (если проект будет на GitHub/GitLab).

---

## FAQ (частые вопросы)

- **Нужен ли отдельный сервер БД?**  
  Нет, сейчас используется локальный файл SQLite (`charity.db`). Для продакшена лучше перейти на PostgreSQL.

- **Можно ли добавить новые типы помощи/категории?**  
  Да, категории задаются в шаблонах и используются как строки в БД — их легко расширить.

- **Как добавить новую роль пользователя?**  
  Потребуется: новая ветка маршрутов (`routes/...`), шаблоны, и логика в `auth.py` + проверка `user_type`.

