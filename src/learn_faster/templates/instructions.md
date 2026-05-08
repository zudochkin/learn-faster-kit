# FASTER Learning System - Instructions

## System Overview

This project uses the FASTER framework:

-   **F**orget: Beginner's mindset
-   **A**ct: Hands-on practice
-   **S**tate: Optimize focus
-   **T**each: Explain to retain
-   **E**nter: Consistency over intensity
-   **R**eview: Adaptive spaced repetition (SM-2 algorithm — intervals adjust to recall quality)

## Directory Structure

```
project-root/
├── CLAUDE.md (this file)
├── .claude/
│   ├── agents/practice-creator.md
│   ├── commands/
│   │   ├── learn.md
│   │   ├── review.md
│   │   └── progress.md
│   └── settings.local.json
└── .learning/
    ├── scripts/
    │   ├── init_learning.py
    │   ├── log_progress.py
    │   ├── review_scheduler.py
    │   ├── concept_quiz.py
    │   ├── journal_logger.py
    │   └── generate_syllabus.py
    ├── references/
    │   └── faster_framework.md
    └── <topic-slug>/
        ├── metadata.json
        ├── syllabus.md
        ├── progress.md
        ├── review_schedule.json
        ├── journal.json
        └── mastery.md
```

## Session Protocol

### EVERY Session Start

The system automatically:

1. Checks for due reviews (via context gathering in commands)
2. Conducts reviews BEFORE new learning if any are due
3. Guides you through the session flow

### Session Flow

```
START
  ↓
[1] Check reviews → Conduct if due
  ↓
[2] State check: "Are you focused?"
  ↓
[3] Present next syllabus item
  ↓
[4] User learns/builds/practices
  ↓
[5] Ask: "Explain it back to me"
  ↓
[6] Log progress → Add to review schedule
  ↓
[7] Remind: "Next session: [time]"
  ↓
END
```

## Script Usage

All scripts are in `.learning/scripts/`. Run from project root.

### Initialize Topic

**User action:** `/learn "Topic Name"`

**Flow:**

```bash
python3 .learning/scripts/init_learning.py "<Topic Name>" .learning
```

→ **Action:** Create comprehensive syllabus tailored to user's level and focus

### Log Progress

```bash
python3 .learning/scripts/log_progress.py <topic-slug> "<summary>" [concept1] [concept2]
```

→ **Action:** Add each concept to review schedule

### Review Management

```bash
# Check status
python3 .learning/scripts/review_scheduler.py status <topic-slug>

# Add concept
python3 .learning/scripts/review_scheduler.py add <topic-slug> "<Concept>"

# Mark reviewed (quality 0-5: 0=blank, 3=correct with effort, 5=perfect)
python3 .learning/scripts/review_scheduler.py review <topic-slug> "<Concept>" <quality>
```

### Journal Logging

```bash
# Log a journal entry (LLM constructs JSON with tags)
python3 .learning/scripts/journal_logger.py log <topic-slug> '<json_payload>'

# Get journal stats (tag distribution, calibration)
python3 .learning/scripts/journal_logger.py stats <topic-slug>

# Recent entries
python3 .learning/scripts/journal_logger.py recent <topic-slug> [count]
```

### Metacognitive Calibration

```bash
# Record quiz with confidence rating
python3 .learning/scripts/concept_quiz.py record <topic-slug> "<Concept>" <correct> [confidence 1-5]

# Get calibration metrics
python3 .learning/scripts/concept_quiz.py calibration <topic-slug>
```

### Topic Info

```bash
# List all topics
python3 .learning/scripts/generate_syllabus.py list

# Get topic details
python3 .learning/scripts/generate_syllabus.py info <topic-slug>
```

## Execution Rules

**✅ ALWAYS:**

1. Check reviews at session start
2. Parse JSON output from scripts
3. Follow `next_action` and `llm_directive` fields
4. Prompt user to teach concepts back
5. Log every learning activity
6. Add learned concepts to review schedule
7. Generate comprehensive syllabi (not minimal)

**❌ NEVER:**

1. Skip review checks
2. Let user passively consume
3. Forget to log progress
4. Skip adding concepts to reviews
5. Generate minimal syllabi

## Workflow Pattern

```
[RUN SCRIPT] → [EXECUTE DIRECTIVE] → [RESPOND TO USER]
```

## Generating Syllabus

When `next_action: "generate_syllabus"`:

1. **Read** `.learning/<topic-slug>/syllabus.md` (created by init script)
2. **Replace placeholder** with comprehensive syllabus tailored to user's level and focus
3. **Include sections**: Overview, Prerequisites, Learning Objectives, 3-4 Phases with 🔨 hands-on projects, Teaching Milestones, Resources, Success Criteria
4. **Update metadata**: Set `"syllabus_generated": true` in `.learning/<topic-slug>/metadata.json`

## Teaching Prompts

After learning concepts, use `AskUserQuestion` to prompt teach-back:

```json
{
    "question": "Ready to teach back what you just learned?",
    "header": "Teach Back",
    "multiSelect": false,
    "options": [
        {
            "label": "Yes, let me explain",
            "description": "I'll explain the concept in my own words"
        },
        {
            "label": "Need review first",
            "description": "Want to review the concept again"
        },
        {
            "label": "Not sure yet",
            "description": "Need more practice before explaining"
        }
    ]
}
```

If user chooses "Yes, let me explain":

-   "Explain [concept] in your own words"
-   "How would you teach this to a beginner?"
-   "What analogy would you use?"

## Progress Tracking

**Milestones:**

-   Every 5 sessions: Show progress report
-   Weekly: Full review of trajectory
-   When stuck: Review learned concepts, identify gaps

**Check session count:**

```bash
cat .learning/<topic-slug>/metadata.json | grep total_sessions
```

**Recent progress:**

```bash
tail -30 .learning/<topic-slug>/progress.md
```

## Key Principles for This System

-   Use `AskUserQuestion` to gather learning preferences
-   Always prompt user to teach concepts back

**For User:**

-   1 project = 1 learning goal
-   30min daily > 3hr weekly (consistency over intensity)
-   Active learning > passive consumption
-   Teaching = best retention
-   Trust the spaced repetition system

# Journal Logging Extension

## Purpose

The structured journal captures user's active thinking with cognitive tags for analytics.

Storage: `.learning/<topic-slug>/journal.json` (structured JSON, not markdown).

------------------------------------------------------------------------

## WHEN to Log

Log ONLY when user is responding to:

-   Teach-back prompts
-   Self-explanation checkpoints
-   Elaborative interrogation ("why/how" answers)
-   Reflection questions
-   Exercises and assignments
-   Review recall attempts
-   Practice tasks

❌ Do NOT log: questions, commands, short confirmations, navigation.

------------------------------------------------------------------------

## HOW to Log

1. Classify user response with tags (pick all that apply):

   - `insight` — new understanding formulated
   - `belief_change` — revised a prior belief
   - `misconception` — revealed misunderstanding
   - `personal_connection` — linked to personal experience
   - `analogy` — created analogy or metaphor
   - `struggle` — difficulty, uncertain response
   - `mastery` — confident, deep explanation
   - `transfer` — applied to new context
   - `self_correction` — caught and fixed own error
   - `question` — asked a deep question

2. Construct JSON and call:

``` bash
python3 .learning/scripts/journal_logger.py log <topic-slug> '{
  "concept": "<concept name>",
  "prompt_type": "<teach_back|self_explanation|elaborative|reflection|application|review>",
  "prompt": "<exact AI question>",
  "user_response": "<EXACT user words — DO NOT modify>",
  "tags": ["<tag1>", "<tag2>"],
  "session": <number>,
  "phase": "<phase name>",
  "confidence_before": <1-5 or null>,
  "quality_after": <0-5 or null>
}'
```

------------------------------------------------------------------------

## CRITICAL RULE: Preserve Raw Thinking

The `user_response` field stores EXACT text. DO NOT rewrite, summarize, improve, or correct.

------------------------------------------------------------------------

## Example

**AI:** Explain Sartre's bad faith in your own words

**User:** Bad faith is when I lie to myself to avoid responsibility. I see this when I say "I'll start Monday."

→ Tags: `insight`, `personal_connection`

``` bash
python3 .learning/scripts/journal_logger.py log existentialism '{
  "concept": "mauvaise foi",
  "prompt_type": "teach_back",
  "prompt": "Explain Sartre'\''s bad faith in your own words",
  "user_response": "Bad faith is when I lie to myself to avoid responsibility. I see this when I say I'\''ll start Monday.",
  "tags": ["insight", "personal_connection"],
  "session": 3,
  "phase": "Foundations",
  "confidence_before": 4,
  "quality_after": 5
}'
```

------------------------------------------------------------------------

## Automatic Behavior

This process must happen silently. DO NOT tell user you logged it.
