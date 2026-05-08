#!/usr/bin/env python3
"""
Generate quick conceptual multiple-choice quizzes based on least-reviewed concepts.
Called after progress logging to reinforce learning.
"""

import json
from pathlib import Path
from datetime import datetime


def get_least_asked_concepts(topic_slug: str, limit: int = 3, base_dir: str = ".learning"):
    """
    Get the least-asked concepts that need reinforcement.

    Args:
        topic_slug: Slug of the topic
        limit: Number of concepts to return (default 3)
        base_dir: Base directory for learning data

    Returns:
        List of concept dictionaries with review data
    """
    topic_dir = Path(base_dir) / topic_slug
    concepts_dir = topic_dir / "concepts"

    if not concepts_dir.exists():
        return []

    concepts = []
    for concept_file in concepts_dir.glob("*.json"):
        with open(concept_file, "r") as f:
            data = json.load(f)
            concepts.append({
                "concept": data["concept"],
                "slug": data["concept_slug"],
                "review_count": data.get("review_count", 0),
                "last_reviewed": data.get("last_reviewed"),
                "learned_date": data.get("learned_date")
            })

    # Sort by review_count (ascending) then by learned_date (oldest first)
    concepts.sort(key=lambda x: (x["review_count"], x["learned_date"]))

    return concepts[:limit]


def generate_quiz_directive(topic_slug: str, base_dir: str = ".learning"):
    """
    Generate LLM directive for creating MC questions about least-asked concepts.

    Args:
        topic_slug: Slug of the topic
        base_dir: Base directory for learning data

    Returns:
        JSON output with quiz directive for LLM
    """
    concepts = get_least_asked_concepts(topic_slug, limit=3, base_dir=base_dir)

    if not concepts:
        output = {
            "status": "no_concepts",
            "quiz_needed": False,
            "llm_directive": "No concepts available for quiz. Continue with learning."
        }
        print(json.dumps(output, indent=2))
        return

    # Build directive for LLM
    concept_names = [c["concept"] for c in concepts]

    directive = f"""
After logging progress, create a quick conceptual quiz using AskUserQuestion.

Pick ONE concept from these least-reviewed concepts: {', '.join(concept_names)}

Create a multiple-choice question that tests understanding (not memorization):
- Question should test conceptual understanding
- 4 plausible options (one correct, three reasonable distractors)
- After user answers, explain why the correct answer is right and why others are wrong
- Keep it quick (30 seconds to answer)

Example format for AskUserQuestion:
{{
  "question": "What is the main purpose of [concept]?",
  "header": "Quick Quiz",
  "multiSelect": false,
  "options": [
    {{"label": "Option A", "description": "Brief explanation"}},
    {{"label": "Option B", "description": "Brief explanation"}},
    {{"label": "Option C", "description": "Brief explanation"}},
    {{"label": "Option D", "description": "Brief explanation"}}
  ]
}}

After quiz, update the concept's quiz_count in .learning/{topic_slug}/concepts/[concept-slug].json
"""

    output = {
        "status": "quiz_ready",
        "quiz_needed": True,
        "least_reviewed_concepts": concepts,
        "llm_directive": directive.strip(),
        "suggested_prompt": f"Быстрый квиз! Проверим понимание: {', '.join(concept_names)}"
    }

    print(json.dumps(output, indent=2))


def record_quiz_attempt(topic_slug: str, concept: str, correct: bool, confidence: int = None, base_dir: str = ".learning"):
    """
    Record a quiz attempt for a concept with optional confidence rating.

    Args:
        topic_slug: Slug of the topic
        concept: Name of the concept
        correct: Whether the answer was correct
        confidence: Pre-test confidence 1-5 (optional, for metacognitive calibration)
        base_dir: Base directory for learning data
    """
    topic_dir = Path(base_dir) / topic_slug
    concepts_dir = topic_dir / "concepts"

    concept_slug = concept.lower().replace(" ", "-").replace("/", "-")
    concept_file = concepts_dir / f"{concept_slug}.json"

    if not concept_file.exists():
        print(f"❌ Концепция '{concept}' не найдена")
        return False

    with open(concept_file, "r") as f:
        data = json.load(f)

    if "quiz_history" not in data:
        data["quiz_history"] = []

    entry = {
        "timestamp": datetime.now().isoformat(),
        "correct": correct,
    }
    if confidence is not None:
        entry["confidence"] = max(1, min(5, confidence))

    data["quiz_history"].append(entry)

    if "quiz_count" not in data:
        data["quiz_count"] = 0
    data["quiz_count"] += 1

    if "quiz_correct_count" not in data:
        data["quiz_correct_count"] = 0
    if correct:
        data["quiz_correct_count"] += 1

    with open(concept_file, "w") as f:
        json.dump(data, f, indent=2)

    accuracy = (data["quiz_correct_count"] / data["quiz_count"] * 100) if data["quiz_count"] > 0 else 0

    calibration_msg = ""
    if confidence is not None:
        conf_norm = confidence / 5.0
        acc_norm = 1.0 if correct else 0.0
        gap = conf_norm - acc_norm
        if gap > 0.3:
            calibration_msg = " Самоуверенность: уверенность была выше результата."
        elif gap < -0.3:
            calibration_msg = " Ты знаешь больше, чем думаешь!"

    output = {
        "status": "success",
        "concept": concept,
        "correct": correct,
        "confidence": confidence,
        "quiz_count": data["quiz_count"],
        "accuracy": round(accuracy, 1),
        "llm_directive": f"Quiz attempt recorded. {'Great job!' if correct else 'Keep practicing this concept.'}{calibration_msg}",
    }

    print(json.dumps(output, indent=2))
    return True


def get_calibration(topic_slug: str, base_dir: str = ".learning"):
    """
    Compute metacognitive calibration metrics across all concepts.
    """
    topic_dir = Path(base_dir) / topic_slug
    concepts_dir = topic_dir / "concepts"

    if not concepts_dir.exists():
        output = {
            "status": "no_data",
            "llm_directive": "No concept data available for calibration.",
        }
        print(json.dumps(output, indent=2))
        return

    confidences = []
    accuracies = []
    overconfident = []
    underconfident = []

    for concept_file in concepts_dir.glob("*.json"):
        with open(concept_file, "r") as f:
            data = json.load(f)

        history = data.get("quiz_history", [])
        rated = [h for h in history if h.get("confidence") is not None]
        if not rated:
            continue

        concept_name = data.get("concept", concept_file.stem)
        concept_confs = [h["confidence"] for h in rated]
        concept_accs = [1.0 if h["correct"] else 0.0 for h in rated]

        avg_conf = sum(concept_confs) / len(concept_confs)
        avg_acc = sum(concept_accs) / len(concept_accs)

        confidences.extend(concept_confs)
        accuracies.extend(concept_accs)

        conf_norm = avg_conf / 5.0
        if conf_norm - avg_acc > 0.2:
            overconfident.append(concept_name)
        elif avg_acc - conf_norm > 0.2:
            underconfident.append(concept_name)

    if not confidences:
        output = {
            "status": "no_calibration_data",
            "llm_directive": "No confidence-rated quiz attempts yet. Calibration data will appear after quizzes with confidence ratings.",
        }
        print(json.dumps(output, indent=2))
        return

    avg_confidence = round(sum(confidences) / len(confidences), 2)
    avg_accuracy = round(sum(accuracies) / len(accuracies) * 100, 1)
    calibration_gap = round(avg_confidence / 5.0 - sum(accuracies) / len(accuracies), 2)

    output = {
        "status": "success",
        "avg_confidence": avg_confidence,
        "avg_accuracy_pct": avg_accuracy,
        "calibration_gap": calibration_gap,
        "overconfident_concepts": overconfident,
        "underconfident_concepts": underconfident,
        "total_rated_attempts": len(confidences),
        "llm_directive": f"Calibration gap: {calibration_gap:+.2f} (positive=overconfident, negative=underconfident).",
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Generate quiz:   python3 concept_quiz.py generate <topic_slug>")
        print("  Record attempt:  python3 concept_quiz.py record <topic_slug> <concept> <correct> [confidence 1-5]")
        print("  Get calibration: python3 concept_quiz.py calibration <topic_slug>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate" and len(sys.argv) >= 3:
        generate_quiz_directive(sys.argv[2])
    elif command == "record" and len(sys.argv) >= 5:
        concept = sys.argv[3]
        correct = sys.argv[4].lower() in ['true', '1', 'yes']
        confidence = int(sys.argv[5]) if len(sys.argv) >= 6 else None
        record_quiz_attempt(sys.argv[2], concept, correct, confidence=confidence)
    elif command == "calibration" and len(sys.argv) >= 3:
        get_calibration(sys.argv[2])
    else:
        print("❌ Invalid command or missing arguments")
