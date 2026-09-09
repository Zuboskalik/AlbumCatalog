# 02_PLAN.md — Технический план проекта: AlbumCatalog

**Методология:** Spec-Driven Development (SDD)
**Шаг:** 2 — Plan
**Статус:** Draft
**Основано на:** [`docs/01_SPEC.md`](01_SPEC.md)

На этом шаге фиксируется техническая архитектура: структура папок, схема БД на уровне Django ORM,
контракты REST API (запрос/ответ в JSON) и инструкция по локальному запуску. Код приложения
(модели, сериализаторы, компоненты) на этом шаге не пишется — только структура и контракты,
на основе которых на шаге Tasks будет составлена декомпозиция работ.

---

## 1. Архитектура и структура папок

Монорепозиторий с двумя независимыми проектами верхнего уровня — `backend/` и `frontend/`,
взаимодействующими через REST API (JSON поверх HTTP). В разработке — раздельные dev-серверы
(Django на :8000, Vite на :5173) с CORS; в проде frontend собирается статикой и может
отдаваться отдельно (Nginx/CDN) либо через `whitenoise`/Django — решение фиксируется на шаге Tasks.

```
AlbumCatalog/
├── docs/
│   ├── 01_SPEC.md
│   └── 02_PLAN.md
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/                     # Django project (settings/urls/wsgi/asgi)
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── catalog/                    # Django app: вся предметная область каталога
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py                # Artist, Album, Song, AlbumSong
│       ├── serializers.py
│       ├── views.py                 # DRF ViewSets
│       ├── urls.py                  # роуты приложения, подключаемые в config/urls.py
│       ├── admin.py
│       ├── migrations/
│       └── tests/
│           ├── test_models.py
│           └── test_api.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── .env.example
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       │   └── index.ts
│       ├── api/
│       │   ├── client.ts            # настроенный axios-инстанс (baseURL, интерцепторы ошибок)
│       │   ├── artists.ts
│       │   ├── albums.ts
│       │   └── songs.ts
│       ├── stores/                  # Pinia
│       │   ├── artists.ts
│       │   ├── albums.ts
│       │   └── songs.ts
│       ├── views/                   # страницы, подключаемые к роутам
│       │   ├── ArtistListView.vue
│       │   ├── ArtistDetailView.vue
│       │   ├── AlbumListView.vue
│       │   ├── AlbumDetailView.vue
│       │   ├── AlbumFormView.vue
│       │   ├── SongListView.vue
│       │   └── SongDetailView.vue
│       ├── components/              # переиспользуемые UI-компоненты
│       │   └── TrackListEditor.vue  # редактор треклиста внутри формы альбома
│       └── types/
│           └── models.ts            # TS-типы, зеркалящие DRF-сериализаторы
└── docker-compose.yml               # опционально, см. раздел 4.2
```

### 1.1 Backend — технологии

| Компонент | Выбор | Примечание |
|---|---|---|
| Framework | Django 5.x | LTS-совместимая минорная версия фиксируется на шаге Tasks |
| API | Django REST Framework | `ModelViewSet` + `DefaultRouter` |
| БД (dev) | SQLite | файл `backend/db.sqlite3`, без внешних зависимостей |
| БД (prod-ready опция) | PostgreSQL | через `DATABASE_URL` / `dj-database-url`, переключается переменной окружения |
| CORS | `django-cors-headers` | разрешить origin Vite dev-сервера (`http://localhost:5173`) |
| Конфигурация | `.env` (через `python-decouple` или `django-environ`) | секреты и `DEBUG`/`DATABASE_URL` не хардкодятся |

### 1.2 Frontend — технологии

| Компонент | Выбор | Примечание |
|---|---|---|
| Framework | Vue 3 (Composition API, `<script setup>`) | — |
| Сборка | Vite | dev-сервер с HMR, прокси `/api` на Django |
| Роутинг | Vue Router 4 | history mode |
| State | Pinia | по одному стору на сущность (artists/albums/songs) |
| HTTP-клиент | Axios | единый инстанс с `baseURL` и обработкой ошибок DRF |
| UI-кит | Tailwind CSS (базовый вариант) | альтернатива — PrimeVue, если нужны готовые сложные компоненты (таблицы, drag-and-drop); финальный выбор фиксируется в Tasks, не блокирует Plan |
| Язык | TypeScript (рекомендуется) | либо обычный JS — уточняется на шаге Tasks |

---

## 2. Схема базы данных (Django Models)

Ниже — **схема на уровне полей ORM**, не финальный код (это относится к шагу Implement).
Соответствует разделу 2 `01_SPEC.md`.

### 2.1 `Artist`

```python
class Artist(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
```

### 2.2 `Album`

```python
class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="albums"
    )
    release_year = models.PositiveIntegerField()

    songs = models.ManyToManyField(
        "Song", through="AlbumSong", related_name="albums"
    )

    class Meta:
        ordering = ["artist__name", "release_year", "title"]

    def __str__(self):
        return f"{self.title} ({self.release_year})"
```

Валидация диапазона `release_year` (1860 ≤ year ≤ текущий год + 1) реализуется в
`clean()`/`validators=[MinValueValidator, MaxValueValidator]` на модели и дублируется
в DRF-сериализаторе (раздел 3).

### 2.3 `Song`

```python
class Song(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
```

### 2.4 `AlbumSong` (through-модель)

```python
class AlbumSong(models.Model):
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name="album_songs"
    )
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name="album_songs"
    )
    track_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ["album", "track_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["album", "track_number"],
                name="uniq_album_track_number",
            ),
            models.UniqueConstraint(
                fields=["album", "song"],
                name="uniq_album_song",
            ),
        ]

    def __str__(self):
        return f"{self.album} — #{self.track_number} {self.song}"
```

### 2.5 Сводная таблица связей

| Модель | Связь | Тип | on_delete |
|---|---|---|---|
| `Album.artist` | → `Artist` | FK (N:1) | `CASCADE` |
| `AlbumSong.album` | → `Album` | FK (N:1) | `CASCADE` |
| `AlbumSong.song` | → `Song` | FK (N:1) | `CASCADE` |
| `Album.songs` | ↔ `Song` через `AlbumSong` | M2M (`through`) | — |

Все каскадные эффекты соответствуют бизнес-правилу 3.4 из `01_SPEC.md`: удаление `Song`
удаляет только записи `AlbumSong`, сама модель `Album` не страдает, и наоборот.

### 2.6 Индексы

- Неявные индексы на всех FK (`artist_id`, `album_id`, `song_id`) — создаются Django автоматически.
- `UniqueConstraint(album, track_number)` и `UniqueConstraint(album, song)` создают составные
  уникальные индексы — они же обеспечивают быстрый поиск треков конкретного альбома.
- Дополнительный индекс на `Song.title` и `Artist.name` — опционально, для ускорения поиска в UI
  (решается на шаге Tasks, если потребуется `db_index=True` или `Meta.indexes`).

---

## 3. Specification API (REST Endpoints)

Базовый префикс: `/api/`. Формат: JSON. Аутентификация — вне MVP (см. `01_SPEC.md`, раздел 6),
эндпоинты открыты. Коды ответов — стандартные DRF (`200`, `201`, `204`, `400`, `404`).

### 3.1 `/api/artists/` — CRUD

| Метод | URL | Действие |
|---|---|---|
| `GET` | `/api/artists/` | список исполнителей |
| `POST` | `/api/artists/` | создать исполнителя |
| `GET` | `/api/artists/{id}/` | детали исполнителя (+ вложенный список альбомов) |
| `PUT`/`PATCH` | `/api/artists/{id}/` | обновить исполнителя |
| `DELETE` | `/api/artists/{id}/` | удалить исполнителя (каскад на его альбомы) |

**`GET /api/artists/` — ответ:**
```json
[
  { "id": 1, "name": "Queen", "albums_count": 2 },
  { "id": 2, "name": "Pink Floyd", "albums_count": 1 }
]
```

**`POST /api/artists/` — запрос:**
```json
{ "name": "Queen" }
```

**`GET /api/artists/{id}/` — ответ:**
```json
{
  "id": 1,
  "name": "Queen",
  "albums": [
    { "id": 10, "title": "A Night at the Opera", "release_year": 1975 },
    { "id": 11, "title": "Greatest Hits", "release_year": 1981 }
  ]
}
```

**Ошибка валидации (`400`), например пустое имя:**
```json
{ "name": ["Это поле не может быть пустым."] }
```

### 3.2 `/api/albums/` — CRUD, вложенное управление треками

| Метод | URL | Действие |
|---|---|---|
| `GET` | `/api/albums/` | список альбомов (с `artist` как вложенным объектом или `artist_id`) |
| `POST` | `/api/albums/` | создать альбом, опционально сразу с треклистом |
| `GET` | `/api/albums/{id}/` | детали альбома с полным треклистом, отсортированным по `track_number` |
| `PUT`/`PATCH` | `/api/albums/{id}/` | обновить метаданные альбома |
| `DELETE` | `/api/albums/{id}/` | удалить альбом (каскад на `AlbumSong`, песни сохраняются) |
| `GET` | `/api/albums/{id}/tracks/` | список треков альбома (эквивалент вложенного `tracks` из деталей) |
| `POST` | `/api/albums/{id}/tracks/` | добавить трек в альбом (`song_id` + `track_number`, либо `song: {title}` для создания песни "на лету") |
| `PATCH` | `/api/albums/{id}/tracks/{track_id}/` | изменить `track_number` / заменить песню трека |
| `DELETE` | `/api/albums/{id}/tracks/{track_id}/` | удалить трек из альбома (сама `Song` не удаляется) |

**`GET /api/albums/{id}/` — ответ:**
```json
{
  "id": 10,
  "title": "A Night at the Opera",
  "release_year": 1975,
  "artist": { "id": 1, "name": "Queen" },
  "tracks": [
    { "id": 101, "track_number": 1, "song": { "id": 55, "title": "Death on Two Legs" } },
    { "id": 102, "track_number": 11, "song": { "id": 42, "title": "Bohemian Rhapsody" } }
  ]
}
```

**`POST /api/albums/` — запрос (создание альбома сразу с треклистом):**
```json
{
  "title": "A Night at the Opera",
  "artist_id": 1,
  "release_year": 1975,
  "tracks": [
    { "song_id": 55, "track_number": 1 },
    { "song": { "title": "Bohemian Rhapsody" }, "track_number": 11 }
  ]
}
```
Элемент `tracks[]` принимает **либо** `song_id` (привязка существующей песни), **либо** вложенный
объект `song: { "title": "..." }` (создание новой песни "на лету" в рамках той же транзакции).

**`POST /api/albums/{id}/tracks/` — запрос (добавление одного трека):**
```json
{ "song_id": 42, "track_number": 11 }
```

**Ошибка нарушения уникальности `track_number` (`400`):**
```json
{
  "non_field_errors": [
    "Трек с номером 11 уже существует в этом альбоме."
  ]
}
```
или, при валидации на уровне поля:
```json
{ "track_number": ["Album и track_number должны быть уникальны вместе."] }
```

**`GET /api/albums/` — ответ (список, укороченное представление):**
```json
[
  {
    "id": 10,
    "title": "A Night at the Opera",
    "release_year": 1975,
    "artist": { "id": 1, "name": "Queen" },
    "tracks_count": 12
  }
]
```

### 3.3 `/api/songs/` — CRUD + список альбомов песни

| Метод | URL | Действие |
|---|---|---|
| `GET` | `/api/songs/` | каталог песен (с поиском `?search=<q>` по названию) |
| `POST` | `/api/songs/` | создать песню |
| `GET` | `/api/songs/{id}/` | детали песни + список альбомов, в которых она участвует |
| `PUT`/`PATCH` | `/api/songs/{id}/` | обновить название песни |
| `DELETE` | `/api/songs/{id}/` | удалить песню (каскад на `AlbumSong`, альбомы сохраняются) |

**`GET /api/songs/{id}/` — ответ:**
```json
{
  "id": 42,
  "title": "Bohemian Rhapsody",
  "albums": [
    {
      "album": { "id": 10, "title": "A Night at the Opera", "release_year": 1975, "artist": "Queen" },
      "track_number": 11
    },
    {
      "album": { "id": 11, "title": "Greatest Hits", "release_year": 1981, "artist": "Queen" },
      "track_number": 2
    }
  ]
}
```

**`GET /api/songs/` — ответ (список):**
```json
[
  { "id": 42, "title": "Bohemian Rhapsody", "albums_count": 2 },
  { "id": 55, "title": "Death on Two Legs", "albums_count": 1 }
]
```

**`GET /api/songs/?search=bohemian` — поиск по названию, тот же формат ответа, отфильтрованный.**

### 3.4 Общие соглашения по API

- Все `id` — целые числа (`PositiveIntegerField`/`AutoField`).
- Вложенные объекты (`artist`, `song`, `album` внутри других сущностей) в ответах **read-only**;
  для записи используются плоские поля `*_id` (`artist_id`, `song_id`) — стандартный паттерн DRF
  (`PrimaryKeyRelatedField(source=...)` или разные сериализаторы для чтения/записи).
- Ошибки валидации всегда возвращаются как `400` с телом `{ "<field>": ["сообщение", ...] }`
  или `{ "non_field_errors": [...] }` — формат по умолчанию для DRF `ValidationError`.
- Пагинация — вне MVP по умолчанию (полные списки), но при необходимости можно включить
  `PageNumberPagination` глобально в `settings.py`; решение фиксируется на шаге Tasks, если
  объём данных потребует.
- CORS: backend разрешает origin `http://localhost:5173` (и переменную окружения для прод-домена
  frontend).

---

## 4. Инструкция по локальному запуску

### 4.1 Вариант A — без Docker (venv + npm)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # опционально, для доступа в /admin/
python manage.py runserver 8000
```
Backend доступен на `http://localhost:8000/`, API — на `http://localhost:8000/api/`,
Django admin — на `http://localhost:8000/admin/`.

**Frontend (в отдельном терминале):**
```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev
```
Frontend доступен на `http://localhost:5173/`, dev-сервер Vite проксирует запросы `/api`
на Django (настраивается в `vite.config.ts`) либо обращается к нему напрямую через
`VITE_API_BASE_URL` и `axios`.

### 4.2 Вариант B — Docker Compose (опционально)

Предполагаемая структура `docker-compose.yml` (детали фиксируются на шаге Tasks/Implement):

```yaml
services:
  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    ports: ["8000:8000"]
    volumes: ["./backend:/app"]
    env_file: ./backend/.env
    depends_on: [db]

  frontend:
    build: ./frontend
    command: npm run dev -- --host
    ports: ["5173:5173"]
    volumes: ["./frontend:/app"]
    env_file: ./frontend/.env

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: albumcatalog
      POSTGRES_USER: albumcatalog
      POSTGRES_PASSWORD: albumcatalog
    volumes: ["pgdata:/var/lib/postgresql/data"]
    ports: ["5432:5432"]

volumes:
  pgdata:
```

```bash
docker compose up --build
```

По умолчанию для локальной разработки (Вариант A) достаточно SQLite — PostgreSQL через
Docker подключается опционально, когда потребуется приблизить окружение к продакшену.

### 4.3 Переменные окружения (черновой список)

**`backend/.env.example`:**
```
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///db.sqlite3
```

**`frontend/.env.example`:**
```
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 5. Следующие шаги SDD

1. **Tasks** (`docs/03_TASKS.md`) — декомпозиция реализации на конкретные задачи: инициализация
   Django/DRF-проекта, миграции, сериализаторы и вьюсеты, инициализация Vue/Vite-проекта, роуты,
   сторы, компоненты форм, тесты backend и (при необходимости) frontend.
2. **Implement** — написание кода согласно `01_SPEC.md` и данному плану.
