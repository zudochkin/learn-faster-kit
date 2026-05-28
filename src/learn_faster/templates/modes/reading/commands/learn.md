---
description: Начать изучение материала (course.md / book.pdf / video.url) или продолжить текущую главу
---

## Context

- course.md в корне: !`test -f course.md && echo "найден" || echo "(нет)"`
- book.pdf в корне:  !`test -f book.pdf && echo "найден" || echo "(нет)"`
- video.url в корне: !`test -f video.url && echo "найден" || echo "(нет)"`
- yt-dlp:            !`which yt-dlp >/dev/null 2>&1 && echo "ok" || echo "не установлен"`
- Learning dir:      !`test -d .learning && echo "есть" || echo "(нет)"`
- Текущая тема:      !`ls .learning 2>/dev/null | grep -v scripts || echo "(нет темы)"`

## Your Task

Source-driven learning: материал уже зафиксирован (course.md, book.pdf или video.url). Твоя задача — провести пользователя через него главу за главой с активным чтением, конспектом и SM-2 повторениями.

### Если уже есть тема в `.learning/` с `syllabus_generated == true`
Ветка **resume**:

1. Прочитай `.learning/<topic>/metadata.json` → `current_chapter`, `total_chapters`, `source_type`.
2. Прочитай `.learning/<topic>/syllabus.md` для отображения статуса глав.
3. Проверь due reviews: `python3 .learning/scripts/review_scheduler.py due <topic-slug>` — если есть, проведи их **до** новой главы.
4. `AskUserQuestion`:

```json
{
  "question": "С возвращением! Что делаем?",
  "header": "Действие",
  "multiSelect": false,
  "options": [
    { "label": "Продолжить главу N", "description": "Текущая глава ещё в процессе" },
    { "label": "Следующая глава", "description": "Перейти к главе N+1" },
    { "label": "Конкретная глава", "description": "Указать номер" },
    { "label": "Только повторение", "description": "Сделать reviews и закрыть" }
  ]
}
```

5. Запусти Active Reading Loop из system prompt для выбранной главы.

### Если темы ещё нет — авто-детект источника

**Только `course.md`** → invoke `@material-loader` с инструкцией `source=course_md, path=course.md`.

**Только `book.pdf`** →
1. Сначала вызови `ListMcpResourcesTool` чтобы убедиться, что pdf-mcp подключён.
2. Если `mcp__pdf-mcp__*` найден → invoke `@material-loader` с `source=book_pdf, path=book.pdf`.
3. Если pdf-mcp не подключён — скажи пользователю:
   > Для работы с PDF нужен pdf-mcp. Запусти:
   > ```
   > pip install pdf-mcp
   > claude mcp add pdf-mcp -- pdf-mcp
   > ```
   > Затем перезапусти меня. Или продолжим с ручным вводом оглавления?
   И предложи через `AskUserQuestion` ручную пасту как fallback.

**Только `video.url`** →
1. Проверь `yt-dlp`: `which yt-dlp >/dev/null 2>&1`.
2. Если найден → invoke `@material-loader` с `source=youtube_video, path=video.url`.
3. Если `yt-dlp` нет — скажи пользователю:
   > Для работы с YouTube нужен yt-dlp:
   > ```
   > brew install yt-dlp        # macOS
   > uv tool install yt-dlp     # cross-platform
   > pipx install yt-dlp        # alternative
   > ```
   > Затем перезапусти меня. Или продолжим с ручным вводом оглавления?
   И предложи через `AskUserQuestion` ручную пасту как fallback.

**Несколько источников найдено** (любая комбинация course.md / book.pdf / video.url) → собери динамический `AskUserQuestion` с одной опцией на каждый найденный файл:

```json
{
  "question": "В корне найдено несколько источников. По какому материалу учимся?",
  "header": "Источник",
  "multiSelect": false,
  "options": [
    { "label": "course.md", "description": "Онлайн-курс (таблица или список ссылок)" },
    { "label": "book.pdf", "description": "Книга через pdf-mcp" },
    { "label": "video.url", "description": "YouTube-видео через yt-dlp" }
  ]
}
```
(показывай только реально найденные опции). По выбору — invoke `@material-loader` с соответствующим `source=...`.

**Ничего нет** → `AskUserQuestion`:

```json
{
  "question": "В корне нет course.md, book.pdf или video.url. Как поступим?",
  "header": "Источник",
  "multiSelect": false,
  "options": [
    { "label": "Вставить оглавление пастой", "description": "Я пришлю список глав/уроков прямо в чат" },
    { "label": "Положу файл и перезапущу", "description": "Закроем сейчас, я положу course.md / book.pdf / video.url и снова /learn" }
  ]
}
```
Если выбрано «пастой» → invoke `@material-loader` с `source=manual`.

### После загрузки материала (от material-loader)

1. Прочитай свежесозданный `syllabus.md` и покажи краткий обзор: «Загружено: <title>, всего глав: N. Готов начать с главы 1?»
2. `AskUserQuestion`:

```json
{
  "question": "С какой главы начнём?",
  "header": "Старт",
  "multiSelect": false,
  "options": [
    { "label": "С главы 1", "description": "Стандартный путь" },
    { "label": "С другой главы", "description": "Назови номер" }
  ]
}
```

3. Запусти Active Reading Loop из system prompt для выбранной главы.

### Бутстрап скелета `.learning/<topic>/`

Перед запуском `@material-loader` (когда темы ещё нет):

1. Получи название курса/книги — либо из `course.md` (первый `#`-заголовок), либо запроси у пользователя через `AskUserQuestion`.
2. Запусти: `python3 .learning/scripts/init_learning.py "<title>" .learning` — это создаст скелет `metadata.json`, `syllabus.md`, `progress.md`, `review_schedule.json`, `mastery.md`.
3. **После** этого вызывай `@material-loader` — он перепишет `syllabus.md` под формат reading и обогатит `metadata.json` полями `mode`, `source_type`, `source_path`, `total_chapters`, `current_chapter`, `chapter_ranges`, `syllabus_generated`.

## Важно

- Не пытайся сам распарсить PDF — это работа `@material-loader` через `mcp__pdf-mcp__*`.
- Не пытайся сам распарсить YouTube или VTT — это работа `@material-loader` и `youtube_loader.py`. Не вызывай `yt-dlp` напрямую из главного coach-а.
- Не генерируй syllabus с нуля — материал зафиксирован, мы идём по нему.
- Перед любой новой главой — проверь due reviews. Reviews первее.
