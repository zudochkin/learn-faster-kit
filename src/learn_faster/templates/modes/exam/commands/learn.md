---
description: Initialize a new learning topic $topic for exam preparation using the FASTER framework
---

## Context

-   Current topic: !`ls .learning/ 2>/dev/null | grep -v scripts`

**Note:** The `.learning/` directory is already initialized. Check the topic folder name (ignore `scripts/`).

## Your Task

Initialize exam-focused learning for the specified topic using the FASTER framework.

**If a topic already exists:**

-   Inform: "Этот проект уже изучает [topic name]"
-   Check for due reviews first (conduct before new learning if any)
-   Continue with current topic (1 project = 1 learning goal)

**If no topic exists yet:**

1. **Gather exam preferences** with `AskUserQuestion` based on users selected topic:
   <example>

```json
[
    {
        "question": "Какая у тебя цель на этом экзамене/сертификации?",
        "header": "Цель",
        "multiSelect": false,
        "options": [
            {
                "label": "Минимально сдать",
                "description": "Просто сдать, 70%+ баллов"
            },
            {
                "label": "Сдать уверенно",
                "description": "Целюсь на 80-85%"
            },
            {
                "label": "Высокий балл",
                "description": "Хочу 90%+ или топ-перцентиль"
            },
            {
                "label": "Максимальный балл",
                "description": "Иду за 100%, полное владение"
            }
        ]
    },
    {
        "question": "Когда экзамен?",
        "header": "Сроки",
        "multiSelect": false,
        "options": [
            {
                "label": "1-2 недели",
                "description": "Интенсивная подготовка"
            },
            {
                "label": "1 месяц",
                "description": "Сфокусированная подготовка"
            },
            {
                "label": "2-3 месяца",
                "description": "Планомерное наращивание"
            },
            {
                "label": "3+ месяца",
                "description": "Долгосрочное освоение"
            },
            {
                "label": "Без дедлайна",
                "description": "В своём темпе"
            }
        ]
    },
    {
        "question": "Какие методы подготовки тебе подходят лучше всего?",
        "header": "Методы",
        "multiSelect": true,
        "options": [
            {
                "label": "Пробные тесты",
                "description": "Имитация экзамена и тесты на время"
            },
            {
                "label": "Карточки",
                "description": "Интервальное повторение"
            },
            {
                "label": "Решение задач",
                "description": "Разбор примеров и кейсов"
            },
            {
                "label": "Объяснение своими словами",
                "description": "Пересказ концепций для закрепления"
            }
        ]
    }
]
```

</example>

2. **Search online first** for real exam syllabus and structure:

    - Use WebSearch to find: "[topic] exam syllabus", "[certification] exam blueprint", "[subject] exam topics"
    - Use WebFetch to analyze official exam guides, topic breakdowns, and weightings
    - Identify: exam format, time limits, passing scores, topic distribution, common difficulty areas

3. Run: `python3 .learning/scripts/init_learning.py "[topic name]" .learning`
4. Parse JSON output and follow `llm_directive`
5. **READ** `.learning/<topic-slug>/syllabus.md` to see the template structure
6. Generate **exam-focused syllabus** based on real exam structure found online
    - Tailor to user's goal and timeline
    - Match actual exam topic distribution and weightings
    - Focus on high-yield topics that appear frequently
7. **Replace** the template placeholders with actual content
8. Update metadata: `"syllabus_generated": true` in `.learning/<topic-slug>/metadata.json`

**Exam-Oriented Syllabus Structure:**

-   **Exam Overview:** Format, sections, time limits, passing score, common difficulty areas
-   **High-Yield Topics:** Topics most likely to appear (based on exam blueprint/frequency)
-   **Study Schedule:** Week-by-week plan based on their timeline
-   **Learning Phases:** Organized by exam sections or topic domains
    -   Each phase has: concepts to master + practice questions + mock test
    -   Include ✅ checkboxes for tracking
-   **Practice Strategy:**
    -   Quick quizzes after each concept
    -   Section practice tests mid-phase
    -   Full mock exams at end of phase
-   **Weak Area Tracking:** System to identify and prioritize review topics
-   **Success Criteria:** Target scores for each section

**Ongoing Learning (when topic already exists and syllabus is generated):**

Before presenting the next syllabus item:

1. **Activate prior knowledge:** "What do you already know about [next concept]?" or "Have you seen this on practice tests?"
2. **Build on their answer:** Connect to what they know or to previously learned items
3. **Follow the Concrete → Abstract → Concrete pattern:** Start with a sample exam question, guide to the underlying rule, apply to a different question format
4. **Apply elaborative interrogation:** For every new fact, ask "Why is this answer correct and others wrong?" before proceeding
5. **Use self-explanation checkpoints:** Pause after each step of multi-step solutions. Do not proceed without explanation.
6. **Use faded guidance automatically:** Worked example → faded example → independent practice per concept

**Important:**

-   Generate comprehensive exam-focused syllabus (not minimal)
-   Include realistic practice test schedule
-   Map content to actual exam format/blueprint if available
-   Build in review cycles (spaced repetition)
-   Include time management strategies
-   Add confidence-building milestones

## After Syllabus Generation

1. **Baseline Assessment:**

    - Create initial diagnostic quiz (10-15 questions)
    - Cover major topic areas at surface level
    - Identify current knowledge level
    - Show user: "Let's see where you're starting from"

2. **Study Plan:**

    - Based on timeline and baseline results
    - Daily/weekly study blocks with specific topics
    - Balance new learning + practice + review
    - Show user the plan and adjust if needed

3. **First Session:**
    - Start with highest-yield topic
    - Quick concept review (15 min)
    - Immediate practice quiz (10 min)
    - Review mistakes together (10 min)
    - Set expectation: "Tomorrow we'll review this + add new material"

## Ongoing Learning Pattern

**Each Study Session:**

1. Review quiz on yesterday's material (10 min)
2. New concept learning (20 min)
3. Practice questions on new concept (15 min)
4. Mistake analysis (10 min)
5. Plan tomorrow's topics (5 min)

**Weekly Pattern:**

-   Days 1-5: New material + daily quizzes
-   Day 6: Full practice test on week's material
-   Day 7: Review weak areas from practice test

**Before Exam (Final Week):**

-   Day 7: Full mock exam
-   Day 6: Review all weak areas
-   Day 5: Timed section practice
-   Day 4: Flash card review (high-yield only)
-   Day 3: Another full mock exam
-   Day 2: Light review of common mistakes
-   Day 1: Confidence-building review, rest

Show progress visually:
"📊 Your Progress: Baseline 65% → Today 75% → Target 85%"

## Motivational Elements

-   Celebrate score improvements
-   Track study streaks
-   Show days until exam with confidence level
-   Compare current vs target scores
-   Highlight mastered topics

**Remember:** This is exam mode. Focus on what gets tested, high-yield studying, and building test-taking confidence. Every session should include active recall testing. Success = passing the exam confidently.
