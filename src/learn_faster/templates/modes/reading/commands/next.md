---
description: Перейти к следующей главе и провести активное чтение
---

## Context

- Текущая тема: !`ls .learning 2>/dev/null | grep -v scripts || echo "(нет темы)"`

## Your Task

Перейти к следующей непройденной главе и запустить Active Reading Loop.

1. Прочитай `.learning/<topic>/metadata.json` → `current_chapter`, `total_chapters`.
2. Прочитай `.learning/<topic>/syllabus.md` чтобы увидеть статусы (`[ ]`, `[~]`, `[x]`).
3. **Проверь due reviews сначала**: `python3 .learning/scripts/review_scheduler.py due <topic-slug>`. Если есть — проведи их до новой главы (вызови сценарий `/review` или процесс ревью inline).
4. Определи следующую главу:
   - Если `current_chapter` имеет статус `[~]` → продолжаем её (а не следующую).
   - Иначе → `current_chapter + 1`.
   - Если все главы `[x]` → поздравь пользователя и предложи `/review` или закрытие темы.
5. Обнови в `syllabus.md` статус выбранной главы на `[~]`.
6. Обнови `metadata.current_chapter` если перешли вперёд.
7. Запусти Active Reading Loop из system prompt для главы N (все 10 шагов).

## Важно

- Не пропускай шаг 1 цикла (prior knowledge) даже если глава кажется лёгкой.
- Не пересказывай содержимое главы — пусть пользователь сам её прочтёт или ты извлечёшь куски, но не дампи целиком.
