---
description: Initialize or continue learning a programming topic $topic using project-based approach
---

## Context

- Current topic: !`ls .learning/ 2>/dev/null | grep -v scripts`

**Note:** The `.learning/` directory is already initialized. Check the topic folder name (ignore `scripts/`).

## Your Task

Initialize learning for the specified programming topic using the FASTER framework with project-based approach.

**If a topic already exists:**

- Inform: "Этот проект уже изучает [topic name]"
- Check for due reviews first (conduct before new learning if any)
- Continue with current topic (1 project = 1 learning goal)

**If no topic exists yet:**

1. **Gather learning preferences** with `AskUserQuestion` based on user's selected topic:
   <example>

```json
[
  {
    "question": "Какого уровня ты хочешь достичь в [topic]?",
    "header": "Уровень",
    "multiSelect": false,
    "options": [
      {"label": "Начинающий", "description": "Основы и базовый синтаксис"},
      {"label": "Средний", "description": "Типовые паттерны и проекты"},
      {"label": "Продвинутый", "description": "Архитектура и оптимизация"},
      {"label": "Эксперт", "description": "Глубокое понимание и лучшие практики"}
    ]
  },
  {
    "question": "Какая у тебя цель обучения?",
    "header": "Цель",
    "multiSelect": true,
    "options": [
      {"label": "Делать проекты", "description": "Учиться через создание реальных приложений"},
      {"label": "Глубокое понимание", "description": "Как всё работает под капотом"},
      {"label": "Лучшие практики", "description": "Паттерны кода для продакшна"},
      {"label": "Подготовка к интервью", "description": "Решение задач и алгоритмы"}
    ]
  }
]
```

</example>

2. Run: `python3 .learning/scripts/init_learning.py "[topic name]" .learning`
3. Parse JSON output and follow `llm_directive`
4. **READ** `.learning/<topic-slug>/syllabus.md` to see the template structure
5. Generate comprehensive syllabus **focused on project-based learning**
6. **Replace** the template placeholders with actual content
7. Update metadata: `"syllabus_generated": true` in `.learning/<topic-slug>/metadata.json`

**Programming Mode Syllabus Guidelines:**

- Structure around building progressively complex projects
- Each phase should include 2-3 concepts + 1-2 🔨 hands-on projects
- Projects should build on previous concepts
- Include testing and debugging at each phase
- Focus on understanding "how it works" not just "how to use it"
- Use checkboxes `- [ ]` for tracking progress

**Ongoing Learning (when topic already exists and syllabus is generated):**

Before presenting the next syllabus item:

1. **Activate prior knowledge:** "What do you already know about [next concept]?" or "Have you used anything similar in other languages?"
2. **Build on their experience:** Connect to their existing code knowledge
3. **Follow the Concrete → Abstract → Concrete pattern:** Start with a specific code example, derive the design pattern, apply to a different codebase
4. **Apply elaborative interrogation:** For every new pattern, ask "Why does this pattern exist?" before proceeding
5. **Use self-explanation checkpoints:** Pause after each implementation step. Do not proceed without explanation.
6. **Use faded guidance automatically:** Worked example → TODO scaffold → independent implementation per concept

**Important:**

- Generate comprehensive, project-focused syllabi
- Every concept should lead to building something
- Include code quality and best practices throughout
