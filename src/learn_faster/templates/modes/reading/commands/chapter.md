---
description: Перейти к конкретной главе по номеру. Использование: /chapter 5
argument-hint: <номер главы>
---

## Context

- Аргумент: $ARGUMENTS
- Текущая тема: !`ls .learning/ 2>/dev/null | grep -v scripts`

## Your Task

Перейти к главе с номером, указанным в `$ARGUMENTS`, и запустить Active Reading Loop.

1. Распарси `$ARGUMENTS` как целое число N.
   - Если не число или пусто → попроси пользователя через AskUserQuestion указать номер из списка глав в syllabus.md.
2. Прочитай `.learning/<topic>/metadata.json` → `total_chapters`.
   - Если N < 1 или N > total_chapters → ошибка, покажи диапазон.
3. Прочитай `.learning/<topic>/syllabus.md`, найди заголовок главы N и её статус.
4. Если глава уже `[x]` (пройдена):
   - `AskUserQuestion`: «Глава N уже пройдена. Перечитать или открыть конспект?» → опции «Перечитать заново», «Показать конспект из `chapters/`», «Отмена».
5. Обнови в `syllabus.md` статус главы N на `[~]`, а старый `[~]` верни на `[ ]` если он был.
6. Обнови `metadata.current_chapter = N`.
7. Запусти Active Reading Loop из system prompt для главы N.

## Важно

- Команда — для прыжков. Если пользователь хочет идти линейно, он использует `/next`.
- Не сбрасывай прогресс других глав, только текущий указатель.
