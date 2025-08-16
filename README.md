# 📊 YouTube Stats CLI (API + Scrape)

Инструмент на Python для получения основных метрик YouTube-видео двумя способами:

1. через официальный **YouTube Data API v3**,
2. через быстрый **scrape** на базе `yt-dlp`.

> Подходит для скриптов, CLI-утилит, аналитики, data-pipelines и ботов.

---

## ✨ Возможности

* Извлечение `videoId` из любых форм URL/ID
* Получение: `title`, `channelTitle`, `publishedAt`, `durationSec`, `viewCount`, `likeCount`, `commentCount`, `thumbnails`
* Два режима работы: **`api`** (точнее, устойчивее) и **`scrape`** (быстрее, без ключа)
* Удобный **CLI** и простые **Python-функции** для встраивания
* Мини-парсер ISO8601 длительности → секунды

---

## 📦 Установка

Требования: **Python 3.8+**

```bash
#Установите зависимости
pip install --upgrade pip
pip install google-api-python-client yt-dlp
```


---

## 🔑 Получение API-ключа (для режима `api`)

1. Создайте проект в Google Cloud Console.
2. Включите **YouTube Data API v3**.
3. Создайте **API Key** и сохраните его.

(Если ключа нет или не хотите использовать API — применяйте режим `scrape`.)

---

## 🚀 Быстрый старт (CLI)

Файл: `youtube_stats.py`

```bash
# Подсказка по использованию
python youtube_stats.py --help

# Режим API (нужен API_KEY)
python youtube_stats.py api <API_KEY> <VIDEO_URL_OR_ID>

# Режим Scrape (без ключа)
python youtube_stats.py scrape <VIDEO_URL_OR_ID>
```

**Примеры:**

```bash
python youtube_stats.py api AIza... https://youtu.be/dQw4w9WgXcQ
python youtube_stats.py scrape dQw4w9WgXcQ
```

**Пример вывода (усечён):**

```json
{
  "videoId": "dQw4w9WgXcQ",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "Never Gonna Give You Up",
  "publishedAt": "1987-10-25T00:00:00Z", 
  "channelId": "...",
  "channelTitle": "RickAstleyVEVO",
  "durationSec": 213,
  "viewCount": 1234567890,
  "likeCount": 9876543,
  "commentCount": 123456,
  "thumbnails": { "...": "..." }
}
```

---

## 🧩 Использование как библиотеки (Python)

```python
from youtube_stats import get_stats_api, get_stats_scrape

# Через официальный API
data_api = get_stats_api(api_key="AIza...", url_or_id="https://youtu.be/dQw4w9WgXcQ")
print(data_api["title"], data_api["viewCount"])

# Через scrape (yt-dlp)
data_scrape = get_stats_scrape("dQw4w9WgXcQ")
print(data_scrape["durationSec"])
```

---

## 🧭 Сравнение режимов

| Критерий         | `api` (YouTube Data API v3) | `scrape` (yt-dlp)                   |
| ---------------- | --------------------------- | ----------------------------------- |
| Требуется ключ   | Да                          | Нет                                 |
| Надёжность полей | Высокая, стабильная схема   | Может различаться по версии/региону |
| Ограничения      | Квоты Google API            | Зависит от изменений фронта YouTube |
| Скорость         | Быстро                      | Очень быстро                        |
| Поля `likeCount` | Может быть `None`           | Есть, если публично доступно        |
| Дата публикации  | `publishedAt` в ISO8601     | `upload_date` в формате `YYYYMMDD`  |

---

## 📚 Поля ответа

Все значения — в `dict`:

| Поле           | Тип           | Описание                                     |
| -------------- | ------------- | -------------------------------------------- |
| `videoId`      | `str`         | Идентификатор видео (11 символов)            |
| `url`          | `str`         | Канонический URL видео                       |
| `title`        | `str`         | Заголовок                                    |
| `publishedAt`  | `str`         | API: ISO8601, Scrape: `YYYYMMDD`             |
| `channelId`    | `str`         | ID канала                                    |
| `channelTitle` | `str`         | Название канала                              |
| `durationSec`  | `int`/`None`  | Длительность в секундах                      |
| `viewCount`    | `int`/`None`  | Просмотры                                    |
| `likeCount`    | `int`/`None`  | Лайки (если доступны)                        |
| `commentCount` | `int`/`None`  | Количество комментариев                      |
| `thumbnails`   | `dict`/`list` | Структура миниатюр (схема зависит от режима) |

---

## 🧠 Детали реализации

* `extract_video_id(url_or_id)` — извлекает `videoId` из разных форм URL/ID
* `iso8601_duration_to_seconds(s)` — упрощённый парсер `PnDTnHnMnS` → секунды
* `get_stats_api(api_key, url_or_id)` — обращается к `videos().list()` с `part=snippet,statistics,contentDetails`
* `get_stats_scrape(url_or_id)` — использует `yt_dlp.YoutubeDL(...).extract_info(...)`
* CLI поддерживает команды:

  * `api <API_KEY> <VIDEO_URL_OR_ID>`
  * `scrape <VIDEO_URL_OR_ID>`

---

## ⚠️ Ограничения и подсказки

* В режиме `api` **likeCount** может быть скрыт YouTube → придёт `None`.
* В режиме `scrape` схема `thumbnails` и некоторые поля могут отличаться между версиями `yt-dlp`.
* Возможны региональные ограничения и возрастные блокировки (оба режима).
* Для массовых запросов учитывайте **квоту** YouTube API и внедряйте **caching/backoff**.
* Сертификаты/SSL: в `scrape` включён `nocheckcertificate=True` для стабильности в некоторых окружениях.

---



Нашли баг или есть идея улучшения? Откройте issue — с радостью посмотрим!
