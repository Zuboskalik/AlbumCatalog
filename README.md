# AlbumCatalog

Веб-приложение для каталогизации музыкальных альбомов, исполнителей и песен. Позволяет вести
справочник исполнителей, создавать альбомы с треклистом и отслеживать, в какие альбомы (и под
каким номером трека) входит каждая песня — одна и та же песня может входить в несколько альбомов
под разными порядковыми номерами.

Полная спецификация: [`docs/01_SPEC.md`](docs/01_SPEC.md). Техническая архитектура и контракты
API: [`docs/02_PLAN.md`](docs/02_PLAN.md). Пошаговый план реализации и статус задач:
[`docs/03_TASKS.md`](docs/03_TASKS.md).

## Стек

| Слой | Технология |
|---|---|
| Backend | Django 5, Django REST Framework |
| База данных | MySQL |
| Frontend | Vue 3 (Composition API), Vite, TypeScript |
| State management | Pinia |
| HTTP-клиент | Axios |
| Роутинг | Vue Router |
| Стили | Tailwind CSS |

## Структура репозитория

```
AlbumCatalog/
├── docs/            # Спецификация, план, декомпозиция задач (SDD)
├── backend/         # Django + DRF API (см. docs/02_PLAN.md, раздел 1.1)
├── frontend/        # Vue 3 + Vite SPA (см. docs/02_PLAN.md, раздел 1.2)
└── scripts/         # Вспомогательные скрипты локального запуска
```

## Локальный запуск

Ниже — полная последовательность действий от `git clone` до рабочего приложения в браузере.

### 0. Клонирование репозитория

```bash
git clone <URL этого репозитория>
cd AlbumCatalog
```

### 1. База данных (MySQL)

Backend настроен на подключение к MySQL. Нужен запущенный локальный сервер MySQL и пустая база
данных. Если её ещё нет — создайте (например, через `mysql -u root -p`):

```sql
CREATE DATABASE python_album_catalog CHARACTER SET utf8mb4;
```

Учётные данные для подключения задаются в `backend/.env` (см. шаг 2) — по умолчанию используются
`DB_USER=mysql` / `DB_PASSWORD=mysql`; при необходимости замените их на данные вашего MySQL-сервера.

### 2. Backend (Django + DRF)

```bash
cd backend
python -m venv .venv

# Windows (Git Bash):
source .venv/Scripts/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# при необходимости отредактируйте backend/.env — имя БД, пользователь, пароль MySQL

python manage.py migrate
python manage.py loaddata sample_data   # тестовые данные, см. раздел «Тестовые данные» ниже
python manage.py createsuperuser        # опционально — для входа в /admin/
python manage.py runserver 8000
```

Backend будет доступен на:
- API: **http://localhost:8000/api/**
- Django admin: **http://localhost:8000/admin/**

Оставьте этот терминал открытым и запустите frontend в отдельном.

### 3. Frontend (Vue 3 + Vite)

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000/api — можно не менять
npm run dev
```

Frontend будет доступен на **http://localhost:5173/**.

Откройте `http://localhost:5173/` в браузере — приложение должно показать список исполнителей
(если выполнялся шаг с `loaddata sample_data`, там уже будут тестовые данные).

### Альтернатива: скрипты в `scripts/`

После того как оба окружения один раз подготовлены (`.venv` и `node_modules` установлены), для
последующих запусков можно использовать готовые скрипты вместо ручных команд:

```bash
# PowerShell
scripts\dev-backend.ps1
scripts\dev-frontend.ps1

# Git Bash / macOS / Linux
scripts/dev-backend.sh
scripts/dev-frontend.sh
```

Каждый скрипт запускает соответствующий dev-сервер (backend на `:8000`, frontend на `:5173`).
Docker-конфигурация в проекте не используется — для локальной разработки она не требовалась.

## Тестовые данные

Чтобы не создавать данные вручную после первого запуска, в репозитории есть Django-fixture с
примером каталога — двумя исполнителями, тремя альбомами и четырьмя песнями, включая ключевой
сценарий спецификации (одна песня в двух альбомах под разными номерами трека):

```bash
cd backend
python manage.py loaddata sample_data
```

Загружает: Queen (*A Night at the Opera*, 1975; *Greatest Hits*, 1981) и Pink Floyd (*The Dark
Side of the Moon*, 1973). Песня «Bohemian Rhapsody» входит в оба альбома Queen — треком №11 в
*A Night at the Opera* и треком №2 в *Greatest Hits*, что сразу демонстрирует связь `Song` ↔
`Album` через `AlbumSong` (см. [`docs/01_SPEC.md`](docs/01_SPEC.md), бизнес-правило 1). Команда
идемпотентна — повторный запуск обновит те же записи, не создавая дублей.

## Тесты

Backend покрыт 56 тестами (модели + REST API):

```bash
cd backend
source .venv/Scripts/activate   # или .venv\Scripts\Activate.ps1 на Windows PowerShell
python manage.py test catalog
```

Ожидаемый результат — `OK`. Frontend не имеет отдельного тестового набора; корректность сборки и
типов проверяется через:

```bash
cd frontend
npm run build
```

## Соответствие спецификации (`docs/01_SPEC.md`, раздел 5)

Ниже — сверка выполненной реализации с Acceptance Criteria из спецификации. Полная трассировка по
задачам — в [`docs/03_TASKS.md`](docs/03_TASKS.md) (столбец «Фактический статус» каждой фазы).

### Backend

| Критерий | Статус |
|---|---|
| Модели `Artist`/`Album`/`Song`/`AlbumSong`, миграции применяются | ✅ |
| DB constraint уникальности (`album`, `track_number`) | ✅ |
| DB constraint уникальности (`album`, `song`) | ✅ |
| Дубликат `track_number` → `400`, не `500` | ✅ (покрыто тестом + вручную) |
| REST-эндпоинты Artists/Albums/Songs (CRUD) + вложенный `tracks` | ✅ |
| `GET /api/songs/{id}/` возвращает альбомы песни с номерами треков | ✅ |
| Каскад: удаление `Artist` → удаляет его альбомы и треки | ✅ |
| Каскад: удаление `Song` → удаляет только треки, альбомы остаются | ✅ |
| Каскад: удаление `Album` → песни не удаляются | ✅ |
| Валидация `release_year` и `track_number >= 1` на уровне API | ✅ |
| Автотесты: создание, уникальность, каскады, альбомы песни | ✅ (56 тестов) |
| API задокументировано | ✅ (`docs/02_PLAN.md`, раздел 3 + этот README) |

### Frontend

| Критерий | Статус |
|---|---|
| `npm run dev`/`build` без ошибок консоли | ✅ |
| CRUD исполнителей: список, создание, редактирование, удаление с подтверждением | ✅ |
| CRUD альбомов, включая треки (существующие и новые песни) с номером в форме | ✅ |
| Клиентская валидация дублей номеров треков + читаемая серверная ошибка | ✅ |
| Каталог песен + страница песни со всеми альбомами и номерами треков | ✅ |
| Все данные через Pinia-сторы (без прямых fetch в компонентах) | ✅ |
| Состояния loading/empty/error | ✅ |
| Предупреждение о каскадных последствиях при удалении | ✅ |
| Базовая адаптивность, без явных визуальных поломок | ✅ (Tailwind, десктоп) |

Отклонений от MVP-объёма спецификации нет; всё, что не входит в реализацию (аутентификация,
загрузка обложек, i18n и т.д.), явно вынесено в раздел 6 «Out of Scope» [`docs/01_SPEC.md`](docs/01_SPEC.md)
и не являлось частью требований.
