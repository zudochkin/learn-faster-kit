---
description: Show detailed progress report for current learning topic
---

## Context

- Learning directory: !`ls -d .learning 2>/dev/null`
- Current topic: !`ls .learning/ 2>/dev/null`

**Note:** If `.learning/` doesn't exist, inform user to run `/learn [topic]`. Check topic folders (ignore `scripts/`).

**Note:** After getting topic slug, read the necessary files:

- `.learning/<topic-slug>/metadata.json`
- `.learning/<topic-slug>/progress.md` (last 30 lines)
- `.learning/<topic-slug>/syllabus.md`
- `.learning/<topic-slug>/review_schedule.json`

## Your Task

Generate an encouraging progress report showing learning journey and next steps.

**If no `.learning/`:**

- Inform: "Обучение ещё не начато. Используй `/learn [тема]` чтобы начать!"

**Calculate metrics:**

- Sessions completed (from metadata)
- Days since start (from created_at)
- Concepts learned (count from progress.md)
- Syllabus progress (checked `[x]` vs total `[ ]`)
- Reviews completed (from review_schedule.json)
- Current phase (from syllabus position)

**Present report:**

```markdown
📊 Отчёт о прогрессе: [Topic Name]

🎯 Обзор
Сессий: [N] | Дней: [N] | Фаза: [X] - [Name]
Программа: [X]% ([M]/[Total] пунктов)

📚 Изученные концепции
✓ [Concept 1]
✓ [Concept 2]
... ([N] всего)

🎉 Последние достижения

- [Achievement 1]
- [Achievement 2]

📅 Статистика повторений
Завершено: [N] | Запланировано: [N]
Следующее повторение: [date] ([N] концепций)

🧠 Инсайты обучения
Записей: [N] | Теги: insight ([N]), mastery ([N]), struggle ([N])
Калибровка: уверенность [X] vs качество [Y] (разрыв: [Z])
Тренд: [recent dominant tags]

🎯 Следующие шаги

1. [Next unchecked item]
2. [Next unchecked item]

💡 Наблюдения
[Personalized based on data]
```

**Celebrate milestones:**

- 5 sessions: "🎉 Набираем обороты!"
- 10 sessions: "🔥 Серьёзный настрой!"
- 25%: "🎯 Четверть пути!"
- 50%: "🚀 Половина пройдена!"
- 75%: "⭐ Почти освоено!"
- 100%: "🏆 Программа завершена!"

**Consistency tracking:**

- 3-day streak: "Отлично! 3 дня подряд!"
- 7-day: "🔥 Неделя без пропусков!"
- 14-day: "🌟 Две недели подряд!"
- 30-day: "🏅 Месяц!"

**Data sources for Learning Insights:**

- Run `python3 .learning/scripts/journal_logger.py stats <topic-slug>` for tag distribution, calibration gap, and trends
- Run `python3 .learning/scripts/concept_quiz.py calibration <topic-slug>` for overconfident/underconfident concepts
- If calibration gap > 0.15: suggest "Стоит больше проверять себя перед тем, как двигаться дальше"
- If calibration gap < -0.15: suggest "Ты знаешь больше, чем думаешь — доверяй себе"

**After report:**

- Suggest next actions
- Offer options: continue learning, do reviews, or break
- Keep encouraging tone

**Key:** Progress reports should motivate, not just inform. Celebrate wins, show growth, suggest forward momentum.
