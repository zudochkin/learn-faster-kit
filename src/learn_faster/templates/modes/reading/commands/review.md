---
description: Conduct spaced repetition review session for learned concepts
---

## Context

- Learning directory: !`ls -d .learning 2>/dev/null`
- Current topic: !`ls .learning/ 2>/dev/null`

**Note:** If `.learning/` doesn't exist, inform user to run `/learn [topic]`. Check topic folders (ignore `scripts/`).

## Your Task

Conduct spaced repetition reviews to combat forgetting and reinforce learning.

**If no `.learning/`:**

- Inform: "Обучение не начато. Используй `/learn [тема]` чтобы начать!"

**If reviews due:**

For each concept in review list:

1. **Confidence check** before testing — use `AskUserQuestion`:
   ```json
   {
     "question": "Перед проверкой [Concept]: насколько ты уверен(а)?",
     "header": "Уверенность",
     "multiSelect": false,
     "options": [
       { "label": "1 — Совсем не уверен(а)", "description": "Скорее всего ошибусь" },
       { "label": "2 — Не очень уверен(а)", "description": "Шансы 30-40%" },
       { "label": "3 — 50/50", "description": "Как монетку подбросить" },
       { "label": "4 — Довольно уверен(а)", "description": "Думаю, что знаю" },
       { "label": "5 — Полностью уверен(а)", "description": "Могу объяснить другому" }
     ]
   }
   ```
2. **Retrieval prompt** — vary format based on the concept's `review_count % 4`:
   - **Free recall** (% 4 == 0): "Без подсказок: что ты помнишь о [concept]?"
   - **Cued recall** (% 4 == 1): "Вот связанная тема: [related]. Как [concept] с ней связан?"
   - **Application transfer** (% 4 == 2): "Новый сценарий: [novel problem]. Как бы ты применил(а) [concept]?"
   - **Recognition + justification** (% 4 == 3): Present AskUserQuestion with 4 options, then ask: "Объясни, почему этот ответ верный, а остальные — нет."
3. Listen to user's explanation
4. **Evaluate and assign quality 0-5 internally:**
   - Clear, accurate, fluent → quality 5. Praise.
   - Correct with minor hesitation → quality 4
   - Correct but significant effort/hints needed → quality 3
   - Incorrect but recognized after hints → quality 2. Guide to fill gaps.
   - Incorrect, needed re-teaching → quality 1. Gently correct.
   - Complete blank → quality 0. Review concept before continuing.
5. **Calibration feedback:** Compare confidence to quality. "Ты оценил(а) себя на 4 и справился(лась) — хорошая калибровка!" or "Ты оценил(а) на 5, но были затруднения — давай разберёмся почему."
6. Mark reviewed with quality: `python3 .learning/scripts/review_scheduler.py review <topic-slug> "[Concept]" <quality>`
7. **Log to journal silently:** `python3 .learning/scripts/journal_logger.py log <topic-slug> '<json>'` with prompt_type "review", user_response (exact), tags, confidence_before, quality_after

**After all reviews:**

- Celebrate: "Отлично! Повторено N концепций! 🎉"
- Show next review date
- Use `AskUserQuestion` for next action:

```json
{
  "question": "Что хочешь делать дальше?",
  "header": "Далее",
  "multiSelect": false,
  "options": [
    {
      "label": "Учить новое",
      "description": "Продолжить по программе"
    },
    {
      "label": "Практика",
      "description": "Поработать над упражнениями"
    },
    {
      "label": "Перерыв",
      "description": "Вернусь позже"
    }
  ]
}
```

**If no reviews due:**

- Inform: "Сегодня нет запланированных повторений! Следующее: [date]"
- Suggest continuing with new material

**Handling forgotten concepts:**

- Don't give answer immediately
- Provide hints: "Это связано с [context]..."
- If still stuck: Review briefly, reschedule for tomorrow
- Reschedule: `python3 .learning/scripts/review_scheduler.py add <topic-slug> "[Concept]"`

**Key principle:** Active recall (user reconstructs from memory), not passive recognition
