---
description: Initialize a new learning topic $topic for deep conceptual understanding using the FASTER framework
---

## Context

- Current topic: !`ls .learning/ 2>/dev/null | grep -v scripts`

**Note:** The `.learning/` directory is already initialized. Check the topic folder name (ignore `scripts/`).

## Your Task

Initialize theory-focused learning for the specified topic using the FASTER framework.

**If a topic already exists:**

- Inform: "Этот проект уже изучает [topic name]"
- Check for due reviews first (conduct before new learning if any)
- Continue with current topic (1 project = 1 learning goal)

**If no topic exists yet:**

1. **Gather learning preferences** with `AskUserQuestion` based on users selected topic:
   <example>

```json
[
  {
    "question": "Какой глубины понимания ты хочешь достичь?",
    "header": "Глубина",
    "multiSelect": false,
    "options": [
      {
        "label": "Базовый",
        "description": "Ключевые концепции и базовая интуиция"
      },
      {
        "label": "Средний",
        "description": "Как и почему всё работает изнутри"
      },
      {
        "label": "Глубокий",
        "description": "Первые принципы и математические основы"
      },
      {
        "label": "Экспертный",
        "description": "Понимание на уровне исследований, передний край"
      }
    ]
  },
  {
    "question": "Какой стиль изучения концепций тебе ближе?",
    "header": "Стиль",
    "multiSelect": true,
    "options": [
      {
        "label": "Аналогии",
        "description": "Учиться через сравнения и метафоры"
      },
      {
        "label": "Первые принципы",
        "description": "Строить от фундаментальных истин"
      },
      {
        "label": "Визуальные модели",
        "description": "Диаграммы и визуальные представления"
      },
      {
        "label": "Исторический контекст",
        "description": "Почему это появилось, эволюция идей"
      }
    ]
  },
  {
    "question": "Чего ты хочешь добиться?",
    "header": "Цель",
    "multiSelect": false,
    "options": [
      {
        "label": "Глубокое понимание",
        "description": "Построить надёжные ментальные модели"
      },
      {
        "label": "Исследование",
        "description": "Фундамент для дальнейшего изучения"
      },
      {
        "label": "Учить других",
        "description": "Уметь понятно объяснять другим"
      },
      {
        "label": "Чистое любопытство",
        "description": "Просто хочу знать, как это работает"
      }
    ]
  }
]
```

</example>

2. Run: `python3 .learning/scripts/init_learning.py "[topic name]" .learning`
3. Parse JSON output and follow `llm_directive`
4. **READ** `.learning/<topic-slug>/syllabus.md` to see the template structure
5. Generate **concept-focused syllabus** tailored to user's depth and style
6. **Replace** the template placeholders with actual content
7. Update metadata: `"syllabus_generated": true` in `.learning/<topic-slug>/metadata.json`

**Theory-Focused Syllabus Structure:**

- **Conceptual Overview:** Big picture, why this topic matters, key questions it answers
- **Prerequisites:** Concepts you should understand first (with explanations)
- **Core Principles:** The 3-5 fundamental truths everything else builds from
- **Learning Journey:** Organized by conceptual building blocks
  - Each phase: concept → intuition → first principles → mental model → connections
  - Include 🤔 thought experiments and 📊 visualization exercises
  - Include ✅ checkboxes for "I can explain this simply"
- **Concept Map:** How all ideas connect (visual representation in text)
- **Deep Dive Topics:** Optional advanced areas for curious learners
- **Common Misconceptions:** What people get wrong and why
- **Success Criteria:** "I can explain X from first principles" not "I memorized X"

**Ongoing Learning (when topic already exists and syllabus is generated):**

Before presenting the next syllabus item:

1. **Activate prior knowledge:** "What do you already know about [next concept]?" or "What's your current mental model?"
2. **Build on their understanding:** Connect to existing knowledge, note where it's correct and where it needs refinement
3. **Follow the Concrete → Abstract → Concrete pattern:** Start with a real-world phenomenon, derive the principle, apply to a different domain
4. **Apply elaborative interrogation:** For every new principle, ask "Why must this be true?" before proceeding
5. **Use self-explanation checkpoints:** Pause after each reasoning step. Do not proceed without explanation.
6. **Use faded guidance automatically:** Worked derivation → partial proof → independent construction per concept

**Important:**

- Generate comprehensive concept maps (not just lists)
- Include "why" for every concept (not just "what")
- Build logical progression (each concept builds on previous)
- Add thought experiments for testing understanding
- Include edge cases and boundary conditions
- Connect to related concepts across domains

## After Syllabus Generation

1. **Activate Prior Knowledge:**
   - "What do you already know about [topic]?"
   - "What's your current mental model?"
   - Start with their existing understanding
   - Identify misconceptions gently

2. **Build Foundation:**
   - Start with "Why does [topic] exist?"
   - What problem does it solve?
   - What would the world look like without it?
   - Create motivation before mechanism

3. **First Concept Session:**
   - Pick the most foundational concept
   - Build intuition through analogy (15 min)
   - Explore from first principles (20 min)
   - Test understanding with thought experiments (10 min)
   - Have user teach it back (15 min)
   - Create visual representation together

## Ongoing Learning Pattern

**Each Learning Session (60 min):**

1. **Activate** (5 min):
   - Review previous concept
   - "How would you explain [yesterday's concept]?"

2. **Build Intuition** (15 min):
   - New concept introduction
   - Real-world analogy
   - "What does this remind you of?"

3. **First Principles** (20 min):
   - Break down to fundamentals
   - "Why must this be true?"
   - Build up the concept logically

4. **Thought Experiments** (10 min):
   - "What if we changed [parameter]?"
   - Test boundaries and edge cases
   - Find where the model breaks

5. **Teach Back** (10 min):
   - User explains in own words
   - Without jargon
   - Using analogy or diagram

**Weekly Pattern:**

- Days 1-3: New concepts with deep exploration
- Day 4: Connect concepts, build bigger picture
- Day 5: Revisit concepts from different angles
- Day 6: Teach concepts to someone (or write explanation)
- Day 7: Explore advanced/edge cases or rest

**Monthly Review:**

- Explain entire topic from first principles
- Build complete concept map
- Identify remaining questions
- Explore one deep dive topic

## Practice Creator Integration

After each concept, invoke @practice-creator to generate:

- Thought experiments
- "Explain like I'm 5" challenges
- Edge case exploration exercises
- Concept connection diagrams
- Teaching preparation materials

## Understanding Tracker

Maintain `.learning/<topic-slug>/understanding.md`:

```markdown
## Concept: [Name]

### My Explanation (without looking):

[User's explanation in own words]

### My Mental Model:

[Analogy or visual representation]

### What I'm Still Unsure About:

- [Question 1]
- [Question 2]

### Connections I See:

- Links to [other concept]
- Similar to [analogy]

### Last Reviewed: [Date]

### Confidence: [1-10]
```

## Visualization Prompts

For each major concept, help user create:

- Conceptual diagrams
- Flow charts of logic
- Comparison tables
- Mind maps of connections

Store in `.learning/<topic-slug>/diagrams/`

## Deep Dive Sessions

Periodically offer:

- "Want to explore [advanced topic]?"
- "Let's examine an edge case"
- "What if we question this assumption?"
- "Historical context: how was this discovered?"

## Success Indicators

User is succeeding when they:

- Explain concepts simply without jargon
- Create accurate analogies spontaneously
- Ask "why" questions independently
- Connect new concepts to existing knowledge
- Predict behavior in new scenarios
- Identify assumptions and limitations
- Show genuine curiosity beyond syllabus

## Teaching Moments

Regular prompts:

- "Explain this to a non-technical friend"
- "What's the one-sentence core idea?"
- "Draw a picture of how this works"
- "What real-world example illustrates this?"
- "If you were teaching this, what would you emphasize?"

**Remember:** This is theory mode. Deep understanding over breadth. Quality over quantity. A concept truly mastered can be explained simply, applied flexibly, and connected broadly. Encourage curiosity. Follow interesting threads even if "off syllabus."
