#!/usr/bin/env python3
"""
Structured learning journal with LLM-assigned cognitive tags.
Stores entries as JSON for analytics while preserving raw user responses.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path


VALID_TAGS = [
    "insight",
    "belief_change",
    "misconception",
    "personal_connection",
    "analogy",
    "struggle",
    "mastery",
    "transfer",
    "self_correction",
    "question",
]

VALID_PROMPT_TYPES = [
    "teach_back",
    "self_explanation",
    "elaborative",
    "reflection",
    "application",
    "review",
    "free_recall",
    "cued_recall",
    "recognition",
]


def log_entry(topic_slug: str, payload: dict, base_dir: str = ".learning"):
    topic_dir = Path(base_dir) / topic_slug
    journal_path = topic_dir / "journal.json"

    if not topic_dir.exists():
        output = {
            "status": "error",
            "error": f"Тема '{topic_slug}' не найдена.",
            "llm_directive": "Topic directory does not exist. Initialize it first with /learn.",
        }
        print(json.dumps(output, indent=2))
        return False

    entries = []
    if journal_path.exists():
        with open(journal_path, "r") as f:
            entries = json.load(f)

    tags = payload.get("tags", [])
    tags = [t for t in tags if t in VALID_TAGS]

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "topic_slug": topic_slug,
        "concept": payload.get("concept", ""),
        "prompt_type": payload.get("prompt_type", "teach_back"),
        "prompt": payload.get("prompt", ""),
        "user_response": payload.get("user_response", ""),
        "tags": tags,
        "session": payload.get("session"),
        "phase": payload.get("phase"),
        "review_count": payload.get("review_count"),
        "confidence_before": payload.get("confidence_before"),
        "quality_after": payload.get("quality_after"),
    }

    entries.append(entry)

    with open(journal_path, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    output = {
        "status": "success",
        "entry_id": entry["id"],
        "tags": tags,
        "total_entries": len(entries),
        "llm_directive": "Journal entry recorded. Continue session without mentioning logging to user.",
    }
    print(json.dumps(output, indent=2))
    return True


def get_stats(topic_slug: str, base_dir: str = ".learning"):
    topic_dir = Path(base_dir) / topic_slug
    journal_path = topic_dir / "journal.json"

    if not journal_path.exists():
        output = {
            "status": "no_entries",
            "total_entries": 0,
            "llm_directive": "No journal entries yet. Entries are created after teach-backs and self-explanations.",
        }
        print(json.dumps(output, indent=2))
        return

    with open(journal_path, "r") as f:
        entries = json.load(f)

    if not entries:
        output = {
            "status": "no_entries",
            "total_entries": 0,
            "llm_directive": "No journal entries yet.",
        }
        print(json.dumps(output, indent=2))
        return

    tag_counts = {}
    prompt_type_counts = {}
    confidences = []
    qualities = []

    for e in entries:
        for tag in e.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        pt = e.get("prompt_type", "unknown")
        prompt_type_counts[pt] = prompt_type_counts.get(pt, 0) + 1
        if e.get("confidence_before") is not None:
            confidences.append(e["confidence_before"])
        if e.get("quality_after") is not None:
            qualities.append(e["quality_after"])

    avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else None
    avg_quality = round(sum(qualities) / len(qualities), 2) if qualities else None

    calibration_gap = None
    if avg_confidence is not None and avg_quality is not None:
        conf_normalized = avg_confidence / 5.0
        qual_normalized = avg_quality / 5.0
        calibration_gap = round(conf_normalized - qual_normalized, 2)

    recent = entries[-10:]
    recent_tags = {}
    for e in recent:
        for tag in e.get("tags", []):
            recent_tags[tag] = recent_tags.get(tag, 0) + 1
    recent_tags_trend = sorted(recent_tags, key=recent_tags.get, reverse=True)[:3]

    directive = _build_stats_directive(tag_counts, calibration_gap, recent_tags_trend)

    output = {
        "status": "success",
        "total_entries": len(entries),
        "entries_by_tag": tag_counts,
        "entries_by_prompt_type": prompt_type_counts,
        "avg_confidence": avg_confidence,
        "avg_quality": avg_quality,
        "calibration_gap": calibration_gap,
        "recent_tags_trend": recent_tags_trend,
        "llm_directive": directive,
    }
    print(json.dumps(output, indent=2))


def _build_stats_directive(tag_counts, calibration_gap, recent_trend):
    parts = []

    mastery = tag_counts.get("mastery", 0)
    struggle = tag_counts.get("struggle", 0)
    transfer = tag_counts.get("transfer", 0)
    insight = tag_counts.get("insight", 0)
    misconception = tag_counts.get("misconception", 0)

    if transfer > 3:
        parts.append("User shows strong transfer ability. Consider increasing difficulty.")
    if struggle > mastery and struggle > 3:
        parts.append("User struggling more than mastering. Consider slowing pace or revisiting fundamentals.")
    if insight > 5:
        parts.append("User generating many insights. Encourage deeper exploration.")
    if misconception > 3:
        parts.append("Multiple misconceptions detected. Focus on correcting foundational understanding.")

    if calibration_gap is not None:
        if calibration_gap > 0.15:
            parts.append("User is overconfident (confidence > actual quality). Add more testing before moving forward.")
        elif calibration_gap < -0.15:
            parts.append("User is underconfident. Provide more positive reinforcement and show progress.")

    if "mastery" in recent_trend and "transfer" in recent_trend:
        parts.append("Recent trend shows mastery + transfer. User may be ready for advanced material.")

    return " ".join(parts) if parts else "Continue with current approach."


def get_recent(topic_slug: str, count: int = 5, base_dir: str = ".learning"):
    topic_dir = Path(base_dir) / topic_slug
    journal_path = topic_dir / "journal.json"

    if not journal_path.exists():
        output = {"status": "no_entries", "entries": []}
        print(json.dumps(output, indent=2))
        return

    with open(journal_path, "r") as f:
        entries = json.load(f)

    recent = entries[-count:]
    output = {
        "status": "success",
        "count": len(recent),
        "entries": recent,
        "llm_directive": "Recent journal entries retrieved. Use for context in current session.",
    }
    print(json.dumps(output, indent=2))


def export_markdown(topic_slug: str, base_dir: str = ".learning"):
    topic_dir = Path(base_dir) / topic_slug
    journal_path = topic_dir / "journal.json"
    export_path = Path(base_dir) / "journal.md"

    if not journal_path.exists():
        output = {"status": "no_entries", "llm_directive": "No entries to export."}
        print(json.dumps(output, indent=2))
        return

    with open(journal_path, "r") as f:
        entries = json.load(f)

    lines = ["# Learning Journal\n"]
    for e in entries:
        ts = e.get("timestamp", "")[:16].replace("T", " ")
        lines.append("---\n")
        lines.append(f"## {ts}")
        lines.append(f"Topic: {e.get('topic_slug', '')}")
        lines.append(f"Concept: {e.get('concept', '')}")
        if e.get("tags"):
            lines.append(f"Tags: {', '.join(e['tags'])}")
        lines.append(f"\n### Prompt\n")
        lines.append(e.get("prompt", ""))
        lines.append(f"\n### User Response\n")
        lines.append(e.get("user_response", ""))
        if e.get("confidence_before") or e.get("quality_after"):
            lines.append(f"\n### Metrics\n")
            if e.get("confidence_before"):
                lines.append(f"Confidence: {e['confidence_before']}/5")
            if e.get("quality_after"):
                lines.append(f"Quality: {e['quality_after']}/5")
        lines.append(f"\n### Context\n")
        if e.get("session"):
            lines.append(f"Session: {e['session']}")
        if e.get("phase"):
            lines.append(f"Phase: {e['phase']}")
        lines.append("")

    with open(export_path, "w") as f:
        f.write("\n".join(lines))

    output = {
        "status": "success",
        "exported_to": str(export_path),
        "entry_count": len(entries),
        "llm_directive": f"Exported {len(entries)} entries to {export_path}.",
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Log entry:     python3 journal_logger.py log <topic_slug> '<json_payload>'")
        print("  Get stats:     python3 journal_logger.py stats <topic_slug>")
        print("  Recent:        python3 journal_logger.py recent <topic_slug> [count]")
        print("  Export to md:  python3 journal_logger.py export <topic_slug>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "log" and len(sys.argv) >= 4:
        try:
            payload = json.loads(sys.argv[3])
        except json.JSONDecodeError as e:
            print(json.dumps({"status": "error", "error": f"Invalid JSON: {e}"}))
            sys.exit(1)
        log_entry(sys.argv[2], payload)
    elif command == "stats" and len(sys.argv) >= 3:
        get_stats(sys.argv[2])
    elif command == "recent" and len(sys.argv) >= 3:
        count = int(sys.argv[3]) if len(sys.argv) >= 4 else 5
        get_recent(sys.argv[2], count)
    elif command == "export" and len(sys.argv) >= 3:
        export_markdown(sys.argv[2])
    else:
        print("Invalid command or missing arguments")
