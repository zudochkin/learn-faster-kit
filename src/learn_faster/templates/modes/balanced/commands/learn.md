---
description: Initialize a new learning topic $topic or continue learning an existing one using the FASTER framework
---

## Context

- Current topic: !`ls .learning/ 2>/dev/null | grep -v scripts`

**Note:** The `.learning/` directory is already initialized. Check the topic folder name (ignore `scripts/`).

## Your Task

Initialize learning for the specified topic using the FASTER framework.

**If a topic already exists:**

- Inform: "Этот проект уже изучает [topic name]"
- Check for due reviews first (conduct before new learning if any)
- Continue with current topic (1 project = 1 learning goal)

**If no topic exists yet:**

1. **Gather learning preferences** with `AskUserQuestion` base on users selected topic:
   <example>

```json
[
  {
    "question": "Какого уровня ты хочешь достичь в [topic]?",
    "header": "Уровень",
    "multiSelect": false,
    "options": [
      {
        "label": "Начинающий",
        "description": "Основы и базовые концепции"
      },
      {
        "label": "Средний",
        "description": "Практические навыки и типовые паттерны"
      },
      {
        "label": "Продвинутый",
        "description": "Глубокая экспертиза и граничные случаи"
      },
      {
        "label": "Эксперт",
        "description": "Уровень мастерства, архитектура, оптимизация"
      }
    ]
  },
  {
    "question": "На чём хочешь сфокусироваться?",
    "header": "Фокус",
    "multiSelect": true,
    "options": [
      {
        "label": "Теория",
        "description": "Концепции, принципы, как всё устроено"
      },
      {
        "label": "Практика",
        "description": "Hands-on, проекты, написание кода"
      },
      {
        "label": "Реальный мир",
        "description": "Продакшн-паттерны и лучшие практики"
      },
      {
        "label": "Подготовка к интервью",
        "description": "Типичные вопросы и решение задач"
      }
    ]
  }
]
```

</example>

2. Run: `python3 .learning/scripts/init_learning.py "[topic name]" .learning`
3. Parse JSON output and follow `llm_directive`
4. **READ** `.learning/<topic-slug>/syllabus.md` to see the template structure
5. Generate comprehensive syllabus content **tailored to user's level and focus areas**
6. **Replace** the template placeholders with actual content
7. Update metadata: `"syllabus_generated": true` in `.learning/<topic-slug>/metadata.json`

**Follow the template structure:**

- All sections from the template file (Overview, Prerequisites, Learning Objectives, etc.)
- 3-4 Phases with specific concepts + 🔨 hands-on projects
- Checkboxes `- [ ]` for tracking progress

**Ongoing Learning (when topic already exists and syllabus is generated):**

Before presenting the next syllabus item:

1. **Activate prior knowledge:** "What do you already know about [next concept]?" or "Have you encountered anything similar?"
2. **Build on their answer:** Connect to what they know or to previously learned syllabus items
3. **Follow the Concrete → Abstract → Concrete pattern:** Start with a relatable example, guide to the principle, apply to a new context
4. **Apply elaborative interrogation:** For every new fact, ask "Why is this true?" or "How does this work?" before proceeding
5. **Use self-explanation checkpoints:** Pause after each step of multi-step concepts. Do not proceed without explanation.
6. **Use faded guidance automatically:** Worked example → faded example → independent practice per concept

**Important:**

- Generate comprehensive syllabi (not minimal)
- Include hands-on practice in every phase
