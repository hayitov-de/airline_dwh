Пет проект — DWH на PostgreSQL

Построение хранилища данных по слоям (RAW → STG → DDS → DM) на открытых данных авиаперевозок
([demo-база PostgresPro](https://edu.postgrespro.ru))

## Стек

- **PostgreSQL** — источник и хранилище (два раздельных инстанса)
- **dbt** — трансформации STG / DDS / DM
- **Docker / docker compose** — окружение
- **Python** (uv, psycopg2) — загрузка RAW-слоя

## Реализовано

- **Окружение**: PostgreSQL в Docker, источник и хранилище — раздельные
  контейнеры (`docker-compose.yml`)
- **Слой RAW**: загрузка данных «как есть» из source-базы в хранилище —
  Python-скрипты (`scripts/raw_load_*.py`), по одному на таблицу источника,
  с техническими полями `_loaded_at` / `_source_system`
- **Слой STG**: очистка и приведение типов, разворачивание `jsonb`-полей
  (например, мультиязычных названий) — dbt-модели, материализация `view`
  (`dbt/models/staging/`)

## В разработке (roadmap)

- **Слой DDS** — нормализация 3NF, суррогатные ключи, историчность SCD2
  (`valid_from` / `valid_to`)
- **Слой DM** — витрины данных для аналитики
- **Инкрементальная загрузка** — материализация dbt `incremental` вместо
  полного пересчёта
- **Оркестрация** — DAG в Apache Airflow вместо ручного запуска шагов

## Как запустить

1. Скопировать `.env.example` в `.env` и подставить свои значения:
   ```bash
   cp .env.example .env
   ```
2. Поднять PostgreSQL (source + dwh) в Docker:
   ```bash
   docker compose up -d
   ```
3. Залить demo-базу авиаперевозок в контейнер `source` — дамп доступен на
   [edu.postgrespro.ru](https://edu.postgrespro.ru).
4. Настроить профиль dbt: скопировать `dbt/profiles.yml.example` в
   `~/.dbt/profiles.yml` и
   подставить значения из своего `.env`.
5. Установить Python-зависимости:
   ```bash
   uv sync
   ```
6. Загрузить RAW-слой (каждый скрипт — одна таблица источника):
   ```bash
   uv run scripts/raw_load_airplanes_data.py
   uv run scripts/raw_load_airports_data.py
   # ... и так далее для остальных таблиц в scripts/
   ```
7. Собрать STG-слой:
   ```bash
   cd dbt
   dbt run
   ```

## Структура проекта

```
dwh_demo/
├── dbt/                        # dbt-проект
│   ├── dbt_project.yml
│   ├── profiles.yml.example    # шаблон профиля подключения
│   ├── macros/
│   └── models/
│       └── staging/            # STG-слой (dbt views)
├── scripts/                    # Python-скрипты загрузки RAW-слоя
├── docker-compose.yml          # Postgres source + Postgres dwh
├── .env.example                # шаблон переменных окружения
└── pyproject.toml / uv.lock    # Python-зависимости
```
