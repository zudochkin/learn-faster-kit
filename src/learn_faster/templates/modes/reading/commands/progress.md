---
description: Подробный отчёт о прогрессе по материалу
---

## Context

- Learning directory: !`test -d .learning && echo "есть" || echo "(нет)"`
- Текущая тема: !`ls .learning 2>/dev/null | grep -v scripts || echo "(нет темы)"`

**Note:** Если `.learning/` нет — сообщи пользователю запустить `/learn`. Игнорируй папку `scripts/`.

После получения topic-slug читай:

- `.learning/<topic-slug>/metadata.json`
- `.learning/<topic-slug>/progress.md` (последние 30 строк)
- `.learning/<topic-slug>/syllabus.md`
- `.learning/<topic-slug>/review_schedule.json`
- `.learning/<topic-slug>/chapters/` (список файлов через `ls`)

## Your Task

Сгенерируй мотивирующий отчёт о прогрессе по изучаемому материалу.

**Если темы нет:** «Обучение ещё не начато. Используй `/learn` чтобы загрузить материал!»

**Метрики:**

- Sessions completed (из metadata.total_sessions)
- Days since start (из metadata.created_at)
- Source type (course_md | book_pdf | manual)
- Главы пройдено: посчитай `[x]` в syllabus.md vs `total_chapters`
- Текущая глава: `metadata.current_chapter` + название из syllabus
- Конспектов написано: `ls .learning/<topic>/chapters/ | wc -l`
- Reviews completed: из review_schedule.json (поле reviews с `last_reviewed != null`)
- Due reviews: `python3 .learning/scripts/review_scheduler.py due <topic-slug>`

**Шаблон отчёта:**

```markdown
📚 Прогресс: [Material Title]

🎯 Обзор
Источник: [course.md | book.pdf | ручной ввод]
Сессий: [N] | Дней: [N]
Главы: [M/Total] ([percentage]%)
Текущая: глава [N] — [Title]

📖 Пройденные главы
✓ Глава 1: [Title] ([key idea 1, key idea 2])
✓ Глава 2: [Title] (...)
... ([N] всего)

🧠 Активные карточки SM-2
Всего карточек: [N] | На повторение сегодня: [N]
Следующее повторение: [date] ([N] карточек)

📝 Инсайты обучения
Записей в журнале: [N]
Теги: insight ([N]), mastery ([N]), struggle ([N]), misconception ([N])
Калибровка: уверенность [X] vs качество [Y] (разрыв: [Z])

🎯 Следующие шаги
1. Глава [N+1]: [Title]
2. ...

💡 Наблюдения
[Personalized based on data — e.g., "Сильнее всего цепляют идеи из главы X — ты выделил 3 личные связи"]
```

**Celebrate milestones:**
- 25% глав: «🎯 Четверть пути!»
- 50%: «🚀 Половина пройдена!»
- 75%: «⭐ Почти дочитано!»
- 100%: «🏆 Материал освоен!»

**Consistency streaks:**
- 3 дня подряд: «3 дня подряд!»
- 7 дней: «🔥 Неделя!»
- 14 дней: «🌟 Две недели!»

**Data sources:**
- `python3 .learning/scripts/journal_logger.py stats <topic-slug>` для tag distribution и калибровочного разрыва
- Если calibration gap > 0.15: «Стоит чаще проверять себя перед тем, как объявлять главу пройденной»
- Если < -0.15: «Ты знаешь материал лучше, чем оцениваешь — доверяй себе»

**После отчёта:**
- Предложи действия: продолжить с `/next`, перечитать конкретную через `/chapter N`, повторение `/review`, перерыв
- Тон: тёплый, мотивирующий

**Ключ:** отчёт мотивирует, не просто информирует.
