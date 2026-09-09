# 03_TASKS.md — Декомпозиция задач: AlbumCatalog

**Методология:** Spec-Driven Development (SDD)
**Шаг:** 3 — Tasks
**Статус:** In Progress — Phase 1 (backend-часть), Phase 2 и Phase 3 выполнены
**Основано на:** [`docs/01_SPEC.md`](01_SPEC.md), [`docs/02_PLAN.md`](02_PLAN.md)

Статусы задач: ✅ Done · ⬜ Pending. T1.5–T1.7 (инициализация frontend и общие скрипты запуска)
намеренно оставлены `⬜ Pending` — выполнялась только backend-часть Phase 1 (Django-проект, `.env`,
CORS, роутинг `/api/`), вся Phase 2 и вся Phase 3.

Каждая задача атомарна (один коммит/один PR), имеет явный **Definition of Done (DoD)** и способ
проверки — автотест (TDD, красное → зелёное) либо ручная проверка (`Manual check`). Задачи внутри
фазы выполняются последовательно (нумерация отражает порядок зависимостей); фазы также идут
последовательно, за исключением отдельных задач Phase 5 (документация), которые можно вести
параллельно с Phase 3–4.

Обозначения:
- `[TDD]` — сначала пишется тест (падающий), затем код, который делает его зелёным.
- `[Manual]` — критерий готовности проверяется вручную (глазами / в браузере / curl).
- `[Both]` — есть и автотест, и обязательная ручная проверка.

---

## Phase 1 — Project Setup

Цель фазы: рабочий скелет двух проектов (`backend/`, `frontend/`), которые запускаются локально
и видят друг друга через CORS, без бизнес-логики.

### T1.1 — Инициализация Django-проекта `[Manual]` ✅ Done
- Создать `backend/`, виртуальное окружение, `requirements.txt` (`Django`, `djangorestframework`,
  `django-cors-headers`, `django-environ` или `python-decouple`).
- Выполнить `django-admin startproject config .` внутри `backend/`.
- Создать приложение `catalog`: `python manage.py startapp catalog`, зарегистрировать в
  `INSTALLED_APPS` (`rest_framework`, `corsheaders`, `catalog`).
- **DoD:** `python manage.py runserver` поднимается на `:8000` без ошибок; `python manage.py check`
  завершается без ошибок.

### T1.2 — Конфигурация окружения (.env) `[Manual]` ✅ Done
- Подключить `django-environ`/`python-decouple`, вынести `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`,
  `DATABASE_URL`, `CORS_ALLOWED_ORIGINS` в `.env` (создать `backend/.env.example` из раздела 4.3 `02_PLAN.md`).
- Добавить `backend/.env` в `.gitignore`.
- **DoD:** сервер стартует, читая настройки из `.env`; при отсутствии `.env` — понятная ошибка,
  а не падение с трейсбеком в проде (`DEBUG=False` не крашит `runserver`).

### T1.3 — Настройка CORS `[TDD/Manual]` ✅ Done
- Подключить `corsheaders.middleware.CorsMiddleware` в `MIDDLEWARE` (перед `CommonMiddleware`).
- Настроить `CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")`, по умолчанию включая
  `http://localhost:5173`.
- **DoD (Manual):** запрос `curl -i -H "Origin: http://localhost:5173" http://localhost:8000/api/`
  (после T3.x, когда `/api/` появится) содержит заголовок `Access-Control-Allow-Origin`. На этом
  шаге допустимо проверить на любом временном `GET`-эндпоинте (например, `/admin/login/`).

### T1.4 — Базовый роутинг `/api/` `[Manual]` ✅ Done
- В `config/urls.py` подключить `path("api/", include("catalog.urls"))` и `path("admin/", admin.site.urls)`.
- В `catalog/urls.py` создать пустой `DefaultRouter()` (без вьюсетов пока).
- **DoD:** `GET http://localhost:8000/api/` возвращает `200` с DRF browsable API (пустой список роутов).

### T1.5 — Инициализация Vue 3 + Vite проекта `[Manual]` ⬜ Pending
- Создать `frontend/` через `npm create vite@latest . -- --template vue-ts` (или `vue`, если решено
  без TS — фиксируется здесь на TS согласно `02_PLAN.md`).
- Установить зависимости: `vue-router`, `pinia`, `axios`, Tailwind CSS (`tailwindcss`, `postcss`,
  `autoprefixer`) либо выбранный UI-кит.
- Настроить Tailwind (`tailwind.config.js`, директивы в `src/style.css` или аналог).
- **DoD:** `npm run dev` поднимает Vite на `:5173`, стартовая страница рендерится без ошибок в консоли.

### T1.6 — Каркас Vue Router + Pinia + Axios-клиент `[Manual]` ⬜ Pending
- Подключить `createRouter`/`createPinia` в `src/main.ts`.
- Создать `src/router/index.ts` с заглушками маршрутов: `/artists`, `/albums`, `/songs` (пустые
  компоненты-заглушки).
- Создать `src/api/client.ts` — axios-инстанс с `baseURL = import.meta.env.VITE_API_BASE_URL`.
- Создать `frontend/.env.example` (`VITE_API_BASE_URL=http://localhost:8000/api`) и `frontend/.env`.
- **DoD:** переход по трём маршрутам в браузере рендерит соответствующие заглушки без ошибок консоли;
  `axios`-клиент импортируется без ошибок сборки.

### T1.7 — Скрипты локального запуска и (опционально) Docker Compose `[Manual]` ⬜ Pending
- Добавить в корень README-раздел или отдельный `scripts/` с командами запуска (детали — Phase 5),
  либо сразу `docker-compose.yml` по образцу из `02_PLAN.md` (раздел 4.2), если решено использовать Docker.
- **DoD:** `docker compose up --build` (если используется) поднимает `backend` на `:8000` и `frontend`
  на `:5173` одновременно; либо задокументированы две команды для `venv`/`npm` (проверяется в Phase 5).

**Выход из Phase 1:** оба проекта запускаются локально, CORS настроен, роутинг/сторы — заглушки.

**Фактический статус:** backend-часть (T1.1–T1.4) выполнена — Django-проект `backend/` создан
(Django 5.2, DRF, `django-cors-headers`, `django-environ`, `PyMySQL`), `.env`/`.env.example`
настроены, CORS подтверждён curl-запросом (`Access-Control-Allow-Origin: http://localhost:5173`),
`GET /api/` и `/admin/login/` отвечают `200`. Frontend-часть (T1.5–T1.7) не выполнялась в этом
проходе — переносится на отдельный шаг.

---

## Phase 2 — Backend Core (Models, Migrations, Admin)

Цель фазы: модели данных из `02_PLAN.md` (раздел 2) реализованы, покрыты тестами на уровне ORM,
доступны в Django admin для ручной проверки без API.

### T2.1 — Модель `Artist` `[TDD]` ✅ Done
- Тест: `ArtistModelTest` — создание `Artist(name="Queen")`, проверка `__str__`, проверка, что
  `name` обязателен (`blank=False`).
- Реализация: модель `Artist` в `catalog/models.py` согласно `02_PLAN.md` (раздел 2.1).
- Миграция: `python manage.py makemigrations catalog`.
- **DoD:** тест зелёный; `python manage.py migrate` применяется без ошибок.

### T2.2 — Модель `Song` `[TDD]` ✅ Done
- Тест: создание `Song(title="Bohemian Rhapsody")`, проверка `__str__`, обязательность `title`.
- Реализация модели `Song` (раздел 2.3 `02_PLAN.md`).
- Миграция.
- **DoD:** тест зелёный; миграция применяется.

### T2.3 — Модель `Album` (с FK на `Artist`) `[TDD]` ✅ Done
- Тест: создание `Album` с привязкой к `Artist`; проверка `related_name="albums"`
  (`artist.albums.count() == 1`); проверка обязательности `title`, `artist`, `release_year`.
- Тест на каскад: удаление `Artist` удаляет связанный `Album` (`Album.objects.count() == 0`
  после `artist.delete()`).
- Реализация модели `Album` (раздел 2.2 `02_PLAN.md`), включая `M2M songs через AlbumSong`
  (объявляется, но `AlbumSong` ещё не создана — можно временно закомментировать `through`
  и добавить в T2.4, либо создавать `Album` и `AlbumSong` в одном коммите — решение на исполнителя,
  главное, чтобы тесты обеих моделей были зелёными к концу T2.4).
- Миграция.
- **DoD:** тесты зелёные; каскадное удаление подтверждено тестом.

### T2.4 — Модель `AlbumSong` + constraints уникальности `[TDD]` ✅ Done
- Тест: создание `AlbumSong(album=..., song=..., track_number=1)` — успешно.
- Тест: попытка создать второй `AlbumSong` с тем же `album` и тем же `track_number` (другая песня) —
  вызывает `IntegrityError` при `save()`/`full_clean()` (в зависимости от того, проверяется ли
  constraint на уровне БД или через `validate_unique()`).
- Тест: попытка добавить одну и ту же `song` в один и тот же `album` дважды (разные `track_number`) —
  также вызывает ошибку уникальности (`UniqueConstraint(album, song)`).
- Тест: `track_number = 0` или отрицательный — не проходит валидацию (`full_clean()` поднимает
  `ValidationError` из-за `MinValueValidator(1)`).
- Тест каскада: удаление `Song` удаляет связанный `AlbumSong`, но не удаляет `Album`; удаление
  `Album` удаляет связанный `AlbumSong`, но не удаляет `Song`.
- Реализация модели `AlbumSong` (раздел 2.4 `02_PLAN.md`) с обоими `UniqueConstraint`.
- Миграция.
- **DoD:** все перечисленные тесты зелёные; `python manage.py migrate` применяется без ошибок на
  чистой БД.

### T2.5 — Django Admin для всех моделей `[Manual]` ✅ Done
- Зарегистрировать `Artist`, `Album`, `Song`, `AlbumSong` в `catalog/admin.py`.
- Для `Album` — inline-редактор `AlbumSong` (`TabularInline`), чтобы треки редактировались прямо
  на странице альбома.
- Настроить `list_display`/`search_fields` для удобства (например, `Artist`: `list_display=["name"]`,
  `search_fields=["name"]`; аналогично для `Song`, `Album`).
- **DoD (Manual):** через `python manage.py createsuperuser` → `/admin/` можно создать исполнителя,
  альбом, песню и трек (`AlbumSong`) полностью вручную, включая проверку, что admin **не позволяет**
  сохранить дубликат `track_number` в одном альбоме (показывает ошибку валидации формы).

### T2.6 — Валидация `release_year` на уровне модели `[TDD]` ✅ Done
- Тест: `Album` с `release_year` в будущем (текущий год + 2) не проходит `full_clean()`.
- Тест: `Album` с `release_year=1800` не проходит `full_clean()`.
- Тест: `Album` с корректным годом (например, текущий год) проходит `full_clean()`.
- Реализация: `validators=[MinValueValidator(1860), MaxValueValidator(<текущий_год + 1>)]` на поле
  `release_year` (верхняя граница вычисляется динамически, например через `django.utils.timezone.now().year + 1`
  в функции-валидаторе, а не как константа в момент импорта модуля).
- **DoD:** тесты зелёные.

**Выход из Phase 2:** все модели, миграции и constraints из `02_PLAN.md` реализованы и покрыты
тестами; данные можно полностью администрировать через Django admin без единой строчки API-кода.

**Фактический статус:** ✅ выполнено полностью. Модели `Artist`, `Album`, `Song`, `AlbumSong`
реализованы в [`backend/catalog/models.py`](../backend/catalog/models.py) с обоими
`UniqueConstraint` (`album`+`track_number`, `album`+`song`) и валидацией `release_year`
(1860 … текущий год + 1). Миграция `catalog/migrations/0001_initial.py` применена к MySQL-БД
`python_album_catalog` (`127.0.0.1:3306`, через драйвер PyMySQL). 20 тестов в
[`backend/catalog/tests/test_models.py`](../backend/catalog/tests/test_models.py) зелёные
(`python manage.py test catalog`). Django Admin
([`backend/catalog/admin.py`](../backend/catalog/admin.py)) с `AlbumSongInline` вручную проверен
в браузере: альбом с треками создаётся через inline-форму, повторный `track_number` в одном
альбоме корректно отклоняется с сообщением «Please correct the duplicate data for track_number.».

---

## Phase 3 — Backend REST API (Serializers, Views, ViewSets, API tests)

Цель фазы: REST-контракты из `02_PLAN.md` (раздел 3) реализованы через DRF и покрыты
`APITestCase`.

### T3.1 — `ArtistSerializer` + `ArtistViewSet` (CRUD) `[TDD]` ✅ Done
- Тест (`APITestCase`): `GET /api/artists/` → `200`, пустой список на чистой БД.
- Тест: `POST /api/artists/` с `{"name": "Queen"}` → `201`, объект создан в БД.
- Тест: `POST /api/artists/` с пустым `name` → `400` с сообщением об ошибке по полю `name`.
- Тест: `GET /api/artists/{id}/` → `200`, тело соответствует формату из `02_PLAN.md` (раздел 3.1),
  включая вложенный список `albums` (на этом шаге — пустой, т.к. `Album`-эндпоинтов ещё нет,
  либо создаётся через ORM в `setUp()` теста).
- Тест: `PATCH /api/artists/{id}/` меняет `name` → `200`.
- Тест: `DELETE /api/artists/{id}/` → `204`, объект удалён.
- Реализация: `ArtistSerializer` (list/detail — можно одним сериализатором с `SerializerMethodField`
  для `albums_count`/`albums`), `ArtistViewSet(ModelViewSet)`, регистрация в `catalog/urls.py`
  через `DefaultRouter`.
- **DoD:** все перечисленные тесты зелёные.

### T3.2 — `SongSerializer` + `SongViewSet` (CRUD + поиск) `[TDD]` ✅ Done
- Тест: `GET/POST/PATCH/DELETE /api/songs/` — аналогично T3.1 (список, создание, ошибка валидации
  на пустой `title`, обновление, удаление).
- Тест: `GET /api/songs/?search=bohe` возвращает только песни, чьё название содержит подстроку
  (регистронезависимо).
- Реализация: `SongSerializer`, `SongViewSet` с `filter_backends=[SearchFilter]`, `search_fields=["title"]`.
- **DoD:** тесты зелёные.

### T3.3 — `AlbumSerializer` (read) + `AlbumViewSet` (CRUD метаданных, без треков) `[TDD]` ✅ Done
- Тест: `POST /api/albums/` с `{"title": ..., "artist_id": <id>, "release_year": ...}` (без `tracks`)
  → `201`, объект создан, `artist` в ответе — вложенный объект `{id, name}`.
- Тест: `POST /api/albums/` с несуществующим `artist_id` → `400`.
- Тест: `POST /api/albums/` с `release_year` вне диапазона → `400` (переиспользуется валидатор модели
  либо дублируется в сериализаторе — см. `02_PLAN.md`, бизнес-правило 5).
- Тест: `GET /api/albums/{id}/` → `200`, поле `tracks` присутствует (на этом шаге — пустой список).
- Тест: `GET /api/albums/` → список с укороченным представлением (`tracks_count` вместо полного `tracks`).
- Реализация: `AlbumSerializer` (детальный, с `tracks`), отдельный `AlbumListSerializer` (укороченный,
  если требуется), `AlbumViewSet` с `get_serializer_class` в зависимости от action.
- **DoD:** тесты зелёные.

### T3.4 — Создание альбома сразу с треклистом (`tracks` в `POST /api/albums/`) `[TDD]` ✅ Done
- Тест: `POST /api/albums/` с `tracks: [{"song_id": <id>, "track_number": 1}, ...]` → `201`,
  созданы соответствующие `AlbumSong`.
- Тест: `POST /api/albums/` с `tracks: [{"song": {"title": "New Song"}, "track_number": 1}]` →
  `201`, создана новая `Song` и связанный `AlbumSong` в одной транзакции.
- Тест: `POST /api/albums/` с двумя элементами `tracks`, имеющими одинаковый `track_number` →
  `400`, **ни один** объект (`Album`, `AlbumSong`) не сохранён в БД (проверка атомарности — весь
  запрос обёрнут в `transaction.atomic()`).
- Реализация: кастомный `create()` в `AlbumSerializer` (nested write), оборачивающий создание
  `Album` + `AlbumSong[]` в `transaction.atomic()`, с валидацией уникальности `track_number` внутри
  списка `tracks` ещё до обращения к БД (`validate_tracks()`/`validate()`).
- **DoD:** тесты зелёные, включая проверку отсутствия «частично созданных» альбомов при ошибке.

### T3.5 — Вложенный роут `/api/albums/{id}/tracks/` (список + добавление) `[TDD]` ✅ Done
- Тест: `GET /api/albums/{id}/tracks/` → `200`, список треков альбома, отсортированный по `track_number`.
- Тест: `POST /api/albums/{id}/tracks/` с `{"song_id": <id>, "track_number": N}` → `201`, новый
  `AlbumSong` создан и привязан к альбому из URL.
- Тест: `POST /api/albums/{id}/tracks/` с `track_number`, уже занятым в этом альбоме → `400` с
  сообщением, соответствующим формату из `02_PLAN.md` (раздел 3.2).
- Тест: `POST /api/albums/{id}/tracks/` с `song_id`, который уже есть в этом альбоме → `400`
  (constraint `uniq_album_song`).
- Реализация: либо кастомные `@action(detail=True, methods=["get", "post"])` на `AlbumViewSet`,
  либо отдельный `AlbumTrackViewSet`, вложенный в роутер (`nested_routers` или ручной `path()`) —
  конкретный механизм на усмотрение исполнителя, контракт URL фиксирован в `02_PLAN.md`.
- **DoD:** тесты зелёные.

### T3.6 — `PATCH`/`DELETE` `/api/albums/{id}/tracks/{track_id}/` `[TDD]` ✅ Done
- Тест: `PATCH .../tracks/{track_id}/` меняет `track_number` на свободный номер → `200`.
- Тест: `PATCH .../tracks/{track_id}/` на номер, уже занятый другим треком того же альбома → `400`.
- Тест: `DELETE .../tracks/{track_id}/` → `204`; связанная `Song` **не удаляется** (проверка
  `Song.objects.filter(id=song_id).exists() is True` после удаления трека).
- Тест: обращение к `tracks/{track_id}/`, принадлежащему **другому** альбому (не тому, что в URL) →
  `404`.
- **DoD:** тесты зелёные.

### T3.7 — `GET /api/songs/{id}/` с вложенным списком альбомов `[TDD]` ✅ Done
- Тест: песня, добавленная в 2 альбома с разными `track_number`, при запросе `GET /api/songs/{id}/`
  возвращает оба альбома с соответствующими номерами треков (формат — раздел 3.3 `02_PLAN.md`).
- Тест: песня без единого альбома → `albums: []`.
- Реализация: `SongDetailSerializer` с `SerializerMethodField`/nested `AlbumSongForSongSerializer`,
  использующий `song.album_songs.select_related("album", "album__artist")`.
- **DoD:** тесты зелёные; N+1 запросы отсутствуют (проверяется `assertNumQueries` в тесте или
  вручную через `django-debug-toolbar`/`connection.queries` — на усмотрение исполнителя).

### T3.8 — Каскадное удаление через API `[TDD]` ✅ Done
- Тест: `DELETE /api/artists/{id}/` → связанные `Album` и их `AlbumSong` удалены из БД.
- Тест: `DELETE /api/songs/{id}/` → связанные `AlbumSong` удалены, альбом остаётся (`Album.objects.filter(...).exists() is True`).
- Тест: `DELETE /api/albums/{id}/` → связанные `AlbumSong` удалены, песни остаются.
- **DoD:** тесты зелёные (частично дублируют T2.3/T2.4 на уровне ORM, но здесь — через реальные
  HTTP-запросы к API, что закрывает соответствующий пункт Acceptance Criteria из `01_SPEC.md`).

### T3.9 — Полный прогон backend-тестов + ручная проверка через DRF Browsable API `[Both]` ✅ Done
- Прогнать `python manage.py test catalog` — весь набор тестов из Phase 2–3 зелёный.
- **Manual:** открыть `http://localhost:8000/api/` в браузере, вручную создать исполнителя → альбом
  с треками → песню, убедиться, что DRF browsable API отображает корректные вложенные структуры,
  а ошибка дублирующегося `track_number` показывается как `400` с читаемым сообщением.
- **DoD:** `0 failures` в тестах; ручной сценарий выполнен без ошибок `500`.

**Фактический статус:** `python manage.py test catalog` → **55 тестов, 0 failures** (20 из Phase 2
+ 35 новых API-тестов). Ручной сценарий выполнен через `curl` (эквивалент browsable API): создан
второй альбом «Greatest Hits» с той же песней «Bohemian Rhapsody» под другим `track_number` —
`GET /api/songs/1/` корректно вернул оба альбома с их номерами; попытка добавить трек с уже
занятым `track_number` вернула `400 {"track_number": ["Трек с номером 2 уже существует в этом
альбоме."]}` — без единого `500`.

**Выход из Phase 3:** все REST-эндпоинты из `02_PLAN.md` (раздел 3) реализованы, покрыты
`APITestCase`, вручную проверены через browsable API.

**Фактический статус:** ✅ выполнено полностью. Реализованы
[`backend/catalog/serializers.py`](../backend/catalog/serializers.py) (`ArtistSerializer`/
`ArtistListSerializer`, `SongSerializer`/`SongListSerializer` с вложенным списком альбомов песни
через `SerializerMethodField`, `AlbumSerializer`/`AlbumListSerializer` с nested-записью треков
и `transaction.atomic()`, `AlbumTrackSerializer` с валидацией уникальности `track_number`/`song`
в рамках альбома) и [`backend/catalog/views.py`](../backend/catalog/views.py) (`ArtistViewSet`,
`SongViewSet` с `SearchFilter`, `AlbumViewSet`, плюс `AlbumTrackListCreateView`/
`AlbumTrackDetailView` для вложенного роута `/api/albums/{id}/tracks/{track_id}/`), подключены
в [`backend/catalog/urls.py`](../backend/catalog/urls.py). Ключевое бизнес-правило — одна песня
в разных альбомах с разными `track_number` — покрыто отдельным сквозным тестом
`SongAcrossTwoAlbumsWithDifferentTrackNumbersApiTest` в
[`backend/catalog/tests/test_api.py`](../backend/catalog/tests/test_api.py) и подтверждено
вручную через API. `python manage.py test catalog` → 55/55 тестов зелёные.

---

## Phase 4 — Frontend UI Components

Цель фазы: работающий SPA-интерфейс поверх API из Phase 3, с тремя модулями (Artist, Album, Song)
и явным редактором порядка треков в альбоме.

### T4.1 — TS-типы моделей и API-клиенты `[Manual]`
- Создать `src/types/models.ts`: `Artist`, `Song`, `Album`, `AlbumSong`/`Track` — зеркалят
  сериализаторы из `02_PLAN.md`.
- Создать `src/api/artists.ts`, `src/api/albums.ts`, `src/api/songs.ts` — функции-обёртки над
  `axios`-клиентом (`getArtists()`, `createArtist()`, `getAlbum(id)`, `addTrack(albumId, payload)` и т.д.),
  типизированные через `models.ts`.
- **DoD (Manual):** файлы компилируются без ошибок TypeScript (`npm run build` или `vue-tsc --noEmit`
  проходит).

### T4.2 — Pinia store `artists` `[Manual]`
- `src/stores/artists.ts`: state (`items`, `loading`, `error`), actions (`fetchAll`, `create`,
  `update`, `remove`), использующие `api/artists.ts`.
- **DoD (Manual):** в консоли браузера (Vue Devtools → Pinia) видно, что `fetchAll()` заполняет
  `items` реальными данными с backend.

### T4.3 — Модуль «Исполнители»: список + создание `[Manual]`
- `ArtistListView.vue`: таблица/список исполнителей из `stores/artists`, форма создания нового
  исполнителя (поле `name`), кнопка удаления с `window.confirm`-подтверждением (или модалка).
- Маршрут `/artists` в `router/index.ts` подключает `ArtistListView`.
- **DoD (Manual):** в браузере на `/artists` можно создать исполнителя, увидеть его в списке без
  перезагрузки страницы, удалить его с подтверждением; после удаления список обновляется.

### T4.4 — Модуль «Исполнители»: детальная страница + редактирование `[Manual]`
- `ArtistDetailView.vue` (маршрут `/artists/:id`): показывает имя исполнителя (с inline-редактированием
  или отдельной формой) и список его альбомов (по данным из `GET /api/artists/{id}/`).
- **DoD (Manual):** переход с `/artists` на страницу конкретного исполнителя показывает корректные
  данные; изменение имени сохраняется и отражается в списке `/artists` при возврате.

### T4.5 — Pinia store `songs` + модуль «Песни»: каталог и поиск `[Manual]`
- `src/stores/songs.ts` — аналогично `artists`, плюс action `search(query)`.
- `SongListView.vue` (маршрут `/songs`): список песен, поле поиска (debounce, например 300 мс),
  форма создания песни независимо от альбома.
- **DoD (Manual):** ввод текста в поле поиска фильтрует список через реальный запрос к
  `GET /api/songs/?search=...`; создание песни через форму сразу появляется в списке.

### T4.6 — Модуль «Песни»: детальная страница с альбомами `[Manual]`
- `SongDetailView.vue` (маршрут `/songs/:id`): название песни + список альбомов с номером трека
  в каждом (данные из `GET /api/songs/{id}/`), ссылки на соответствующие страницы альбомов.
- **DoD (Manual):** песня, добавленная в 2+ альбома (проверяется через ранее созданные данные или
  Django admin), корректно показывает оба альбома с правильными номерами треков.

### T4.7 — Pinia store `albums` `[Manual]`
- `src/stores/albums.ts`: state + actions (`fetchAll`, `fetchOne`, `create`, `update`, `remove`,
  `addTrack`, `updateTrack`, `removeTrack`), использующие `api/albums.ts`.
- **DoD (Manual):** actions вызывают корректные эндпоинты (`/api/albums/{id}/tracks/...`) —
  проверяется через вкладку Network в devtools при ручном тестировании T4.9–T4.10.

### T4.8 — Модуль «Альбомы»: список с фильтром по исполнителю `[Manual]`
- `AlbumListView.vue` (маршрут `/albums`): список альбомов (название, исполнитель, год),
  выпадающий фильтр по `artist`, ссылка на детальную страницу и на форму создания.
- **DoD (Manual):** список альбомов отображается корректно; выбор исполнителя в фильтре сужает
  список без перезагрузки страницы.

### T4.9 — Компонент `TrackListEditor.vue` (редактор треклиста) `[Manual]`
- Переиспользуемый компонент: список строк «песня (select существующей ИЛИ поле ввода новой) +
  числовое поле `track_number` + кнопка удаления строки», кнопка «добавить трек».
- Клиентская валидация: подсветка/сообщение об ошибке, если в текущем списке дублируется
  `track_number`, до отправки формы на сервер (соответствует Acceptance Criteria `01_SPEC.md` 5.2).
- **DoD (Manual):** попытка ввести два одинаковых номера трека в форме показывает ошибку и
  блокирует кнопку отправки; после исправления кнопка разблокируется.

### T4.10 — Модуль «Альбомы»: форма создания (`AlbumFormView.vue`) `[Manual]`
- Форма: выбор/поиск исполнителя, `title`, `release_year`, встроенный `TrackListEditor`
  (добавление существующих песен через поиск + создание новых «на лету»).
- Отправка через `stores/albums.create(...)` → `POST /api/albums/` с вложенным `tracks`.
- Обработка серверной ошибки (например, гонка по `track_number`) — понятное сообщение пользователю
  без падения формы.
- **DoD (Manual):** сквозной сценарий — создать нового исполнителя → создать альбом с 3 треками
  (2 существующие песни + 1 новая «на лету») → альбом появляется в `/albums`, треки видны в
  правильном порядке на его странице.

### T4.11 — Модуль «Альбомы»: детальная страница + редактирование треклиста `[Manual]`
- `AlbumDetailView.vue` (маршрут `/albums/:id`): метаданные альбома, треклист (отсортирован по
  `track_number`), кнопки добавления/удаления/изменения номера трека прямо на странице
  (переиспользует `TrackListEditor` или упрощённую inline-версию).
- Удаление альбома — с подтверждением, предупреждающим о каскадном удалении связей (не самих песен).
- **DoD (Manual):** на странице альбома можно удалить трек (песня остаётся в каталоге — проверяется
  переходом на `/songs`), изменить номер трека на свободный (сохраняется), получить ошибку при
  попытке поставить занятый номер.

### T4.12 — Состояния загрузки/ошибок и UX-полировка `[Manual]`
- Во всех трёх модулях (Artists/Albums/Songs): спиннер/скелетон при `loading`, сообщение при
  пустом списке, единообразный вывод ошибок API (используя перехватчик ошибок из `api/client.ts`).
- **DoD (Manual):** отключение backend (остановить `runserver`) при открытом frontend показывает
  пользователю понятное сообщение об ошибке сети на каждой из трёх страниц списков, а не пустой
  экран/necontrolled exception в консоли.

**Выход из Phase 4:** все три UI-модуля из `01_SPEC.md` (раздел 4) реализованы и вручную проверены
сквозными сценариями поверх реального backend.

---

## Phase 5 — Documentation & Integration

Цель фазы: проект воспроизводим «с нуля» человеком, который не участвовал в разработке, по одному
файлу `README.md`.

### T5.1 — `README.md`: обзор проекта `[Manual]`
- Краткое описание (1 абзац) — ссылка на `docs/01_SPEC.md` как источник полной спецификации.
- Таблица стека (backend/frontend) — как в `02_PLAN.md`, раздел 1.
- **DoD (Manual):** README открывается на GitHub/локально и корректно рендерится (markdown без
  битых ссылок на `docs/*.md`).

### T5.2 — `README.md`: пошаговая инструкция локального запуска `[Manual]`
- Раздел «Backend» — команды из `02_PLAN.md` (раздел 4.1): создание venv, `pip install`, `.env`,
  `migrate`, `createsuperuser`, `runserver`.
- Раздел «Frontend» — команды: `npm install`, `.env`, `npm run dev`.
- Раздел «Docker (опционально)» — если Phase 1/T1.7 реализован Docker Compose, привести команду
  `docker compose up --build` и порты по умолчанию.
- Явно указать порты и URL: backend `http://localhost:8000`, API `http://localhost:8000/api/`,
  admin `http://localhost:8000/admin/`, frontend `http://localhost:5173`.
- **DoD (Manual, критично):** выполнить инструкцию **буквально по шагам на чистом клоне репозитория**
  (или в чистом окружении/контейнере) — от `git clone` до открытия `http://localhost:5173` с рабочим
  приложением, без каких-либо шагов «из головы», не описанных в README.

### T5.3 — `README.md`: описание структуры репозитория `[Manual]`
- Краткое дерево папок верхнего уровня (`backend/`, `frontend/`, `docs/`) со ссылками на
  `docs/02_PLAN.md` за подробностями.
- **DoD (Manual):** структура в README соответствует фактической структуре репозитория на момент
  завершения Phase 4 (сверяется вручную).

### T5.4 — `README.md`: раздел про тесты `[Manual]`
- Команда запуска backend-тестов: `python manage.py test catalog` (из `backend/`).
- Если во frontend добавлены автотесты (не обязательно по `01_SPEC.md`/`02_PLAN.md`, но если
  появились в ходе Phase 4) — команда их запуска.
- **DoD (Manual):** команда из README, выполненная в чистом окружении, реально запускает тесты и
  показывает результат `OK`.

### T5.5 — Финальная сверка с Acceptance Criteria из `01_SPEC.md` `[Manual]`
- Пройтись по всем пунктам чек-листов раздела 5.1 (Backend) и 5.2 (Frontend) `01_SPEC.md`,
  отметить каждый как выполненный со ссылкой на задачу(и) из данного файла, которая его закрывает.
- Зафиксировать результат сверки (например, отметками `[x]` прямо в `01_SPEC.md` или отдельной
  таблицей соответствия в конце `README.md` — на усмотрение исполнителя).
- **DoD (Manual):** ни один пункт Acceptance Criteria не остаётся без соответствующей выполненной
  задачи; расхождения либо устраняются, либо явно документируются как сознательно отложенные
  (со ссылкой на раздел 6 «Out of Scope» `01_SPEC.md`).

### T5.6 — CI-проверка (опционально, если требуется репозиторием) `[Manual]`
- Если у проекта есть/предполагается CI (GitHub Actions и т.п.) — настроить минимальный workflow:
  `python manage.py test` для backend, `npm run build`/`vue-tsc --noEmit` для frontend.
- **DoD (Manual):** workflow зелёный на пуше в основную ветку. Если CI не требуется на этом этапе
  проекта — задача помечается как отложенная, без блокировки Phase 5.

**Выход из Phase 5:** проект полностью документирован, воспроизводим с нуля по README, и сверен
с исходной спецификацией.

---

## Сводка зависимостей между фазами

```
Phase 1 (Setup)
   │
   ▼
Phase 2 (Models/Migrations/Admin)
   │
   ▼
Phase 3 (Serializers/Views/API tests)
   │
   ▼
Phase 4 (Frontend UI) ──┐
   │                    │
   ▼                    │
Phase 5 (README/Docs) ◄─┘   (T5.1–T5.3 можно готовить черновиком параллельно с Phase 3–4,
                              но T5.2/T5.5 требуют завершённых Phase 1–4 для реальной проверки)
```

## Следующий шаг SDD

**Implement** — последовательное выполнение задач T1.1 → T5.6 в указанном порядке, с прогоном
тестов/ручных проверок после каждой задачи перед переходом к следующей.
