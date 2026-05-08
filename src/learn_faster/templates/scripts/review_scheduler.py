#!/usr/bin/env python3
"""
Calculate and manage spaced repetition review schedule based on FASTER framework.
"""

import json
import subprocess
import platform
from datetime import datetime, timedelta
from pathlib import Path


# SM-2 algorithm constants
MIN_EF = 1.3
DEFAULT_EF = 2.5
DEFAULT_FIRST_INTERVAL = 1
DEFAULT_SECOND_INTERVAL = 6

# Legacy fallback intervals (used when migrating old review items)
_LEGACY_INTERVALS = [3, 14, 30, 60, 90]


def sm2_calculate(quality: int, repetitions: int, ef: float, interval: int):
    """
    SM-2 algorithm: compute next interval, easiness factor, and repetition count.

    Args:
        quality: Recall quality rating 0-5
        repetitions: Number of successful consecutive reviews
        ef: Current easiness factor
        interval: Current interval in days

    Returns:
        Tuple of (new_interval, new_ef, new_repetitions)
    """
    quality = max(0, min(5, quality))

    if quality < 3:
        return (DEFAULT_FIRST_INTERVAL, ef, 0)

    if repetitions == 0:
        new_interval = DEFAULT_FIRST_INTERVAL
    elif repetitions == 1:
        new_interval = DEFAULT_SECOND_INTERVAL
    else:
        new_interval = round(interval * ef)

    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(MIN_EF, new_ef)

    return (new_interval, new_ef, repetitions + 1)


def add_macos_reminder(concept: str, topic_slug: str, review_date: datetime) -> bool:
    """
    Add a reminder to macOS Reminders app using AppleScript (macOS only).

    Args:
        concept: Name of the concept to review
        topic_slug: Topic slug for reference
        review_date: Date/time for the reminder

    Returns:
        True if reminder was added successfully, False otherwise
    """
    # Only run on macOS
    if platform.system() != "Darwin":
        return False

    try:
        # Format date for AppleScript (e.g., "December 15, 2024 at 9:00:00 AM")
        reminder_date = review_date.strftime("%B %d, %Y at %I:%M:%S %p")

        # Create AppleScript to add reminder
        applescript = f'''
        tell application "Reminders"
            tell list "Learn FASTER"
                make new reminder with properties {{name:"Review: {concept} ({topic_slug})", due date:date "{reminder_date}", body:"Time to review '{concept}' from your {topic_slug} learning. Run /review in Claude Code."}}
            end tell
        end tell
        '''

        # Execute AppleScript
        subprocess.run(
            ["osascript", "-e", applescript],
            check=True,
            capture_output=True,
            text=True
        )
        return True

    except subprocess.CalledProcessError:
        # Reminder list might not exist, try creating it
        try:
            create_list_script = '''
            tell application "Reminders"
                make new list with properties {name:"Learn FASTER"}
            end tell
            '''
            subprocess.run(["osascript", "-e", create_list_script], check=True, capture_output=True)

            # Try adding reminder again
            subprocess.run(["osascript", "-e", applescript], check=True, capture_output=True)
            return True
        except:
            return False
    except Exception:
        return False


def add_review_item(topic_slug: str, concept: str, base_dir: str = ".learning"):
    """
    Add a concept to the review schedule.

    Args:
        topic_slug: Slug of the topic
        concept: Name of the concept to review
        base_dir: Base directory for learning data
    """
    topic_dir = Path(base_dir) / topic_slug
    schedule_path = topic_dir / "review_schedule.json"
    metadata_path = topic_dir / "metadata.json"

    if not schedule_path.exists():
        print(f"❌ Тема '{topic_slug}' не найдена.")
        return False

    with open(schedule_path, "r") as f:
        schedule = json.load(f)

    # Add new review item with SM-2 fields
    learned_date = datetime.now().isoformat()
    next_review_datetime = datetime.now() + timedelta(days=DEFAULT_FIRST_INTERVAL)
    review_item = {
        "concept": concept,
        "learned_date": learned_date,
        "review_count": 0,
        "next_review": next_review_datetime.isoformat(),
        "last_reviewed": None,
        "easiness_factor": DEFAULT_EF,
        "interval": DEFAULT_FIRST_INTERVAL,
        "repetitions": 0,
    }

    schedule["reviews"].append(review_item)

    with open(schedule_path, "w") as f:
        json.dump(schedule, f, indent=2)

    next_review_date = next_review_datetime.strftime("%Y-%m-%d")

    # Check if macOS reminders are enabled in config
    reminder_added = False
    config_path = Path(base_dir) / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)

        if config.get("macos_reminders_enabled", False):
            reminder_datetime = next_review_datetime.replace(hour=9, minute=0, second=0)
            reminder_added = add_macos_reminder(concept, topic_slug, reminder_datetime)

    output = {
        "status": "success",
        "concept": concept,
        "next_review_days": DEFAULT_FIRST_INTERVAL,
        "next_review_date": next_review_date,
        "easiness_factor": DEFAULT_EF,
        "repetitions": 0,
        "macos_reminder_added": reminder_added,
        "llm_directive": "Concept added to review schedule. Use `AskUserQuestion` to ask what they want to do next: continue learning, practice",
        "suggested_response": f"✅ Концепция '{concept}' добавлена в расписание повторений. Первое повторение через {DEFAULT_FIRST_INTERVAL} дн." +
                            (f" 📅 Напоминание в macOS установлено на {next_review_date} в 9:00." if reminder_added else "")
    }

    print(json.dumps(output, indent=2))
    return True


def mark_reviewed(topic_slug: str, concept: str, quality: int = 3, base_dir: str = ".learning"):
    """
    Mark a concept as reviewed using SM-2 adaptive scheduling.

    Args:
        topic_slug: Slug of the topic
        concept: Name of the concept reviewed
        quality: Recall quality 0-5 (0=blank, 3=correct with effort, 5=perfect)
        base_dir: Base directory for learning data
    """
    topic_dir = Path(base_dir) / topic_slug
    schedule_path = topic_dir / "review_schedule.json"

    with open(schedule_path, "r") as f:
        schedule = json.load(f)

    for item in schedule["reviews"]:
        if item["concept"].lower() == concept.lower():
            item["review_count"] += 1
            item["last_reviewed"] = datetime.now().isoformat()

            # Backward compatibility: migrate legacy items missing SM-2 fields
            ef = item.get("easiness_factor", DEFAULT_EF)
            interval = item.get("interval")
            if interval is None:
                idx = min(item["review_count"] - 1, len(_LEGACY_INTERVALS) - 1)
                interval = _LEGACY_INTERVALS[idx]
            repetitions = item.get("repetitions", item["review_count"] - 1)

            new_interval, new_ef, new_reps = sm2_calculate(quality, repetitions, ef, interval)

            item["easiness_factor"] = new_ef
            item["interval"] = new_interval
            item["repetitions"] = new_reps
            item["next_review"] = (datetime.now() + timedelta(days=new_interval)).isoformat()

            with open(schedule_path, "w") as f:
                json.dump(schedule, f, indent=2)

            next_review_date = (datetime.now() + timedelta(days=new_interval)).strftime("%Y-%m-%d")

            difficulty_msg = ""
            if quality < 3:
                difficulty_msg = " Эту тему стоит повторить ещё — запланировано ближайшее повторение."
            elif quality >= 5:
                difficulty_msg = " Отличное вспоминание — интервал увеличен."

            output = {
                "status": "success",
                "concept": concept,
                "review_count": item["review_count"],
                "quality": quality,
                "easiness_factor": round(new_ef, 2),
                "repetitions": new_reps,
                "next_review_days": new_interval,
                "next_review_date": next_review_date,
                "llm_directive": f"Review complete (quality={quality}). Show next review date.{difficulty_msg}",
                "suggested_response": f"✅ '{concept}' — повторение #{item['review_count']} завершено (качество: {quality}/5). Следующее через {new_interval} дн. ({next_review_date}).{difficulty_msg}",
            }

            print(json.dumps(output, indent=2))
            return True

    output = {
        "status": "error",
        "error": f"Concept '{concept}' not found in review schedule",
        "llm_directive": "Inform user the concept wasn't found. Check spelling or list available concepts.",
    }
    print(json.dumps(output, indent=2))
    return False


def get_due_reviews(topic_slug: str, base_dir: str = ".learning"):
    """
    Get list of concepts due for review.

    Args:
        topic_slug: Slug of the topic
        base_dir: Base directory for learning data

    Returns:
        List of concepts due for review
    """
    topic_dir = Path(base_dir) / topic_slug
    schedule_path = topic_dir / "review_schedule.json"

    if not schedule_path.exists():
        return []

    with open(schedule_path, "r") as f:
        schedule = json.load(f)

    now = datetime.now()
    due_reviews = []

    for item in schedule["reviews"]:
        next_review = datetime.fromisoformat(item["next_review"])
        if next_review <= now:
            days_overdue = (now - next_review).days
            due_reviews.append({
                "concept": item["concept"],
                "days_overdue": days_overdue,
                "review_count": item["review_count"]
            })

    return due_reviews


def show_review_status(topic_slug: str, base_dir: str = ".learning"):
    """
    Display review status for a topic with JSON output for LLM parsing.

    Args:
        topic_slug: Slug of the topic
        base_dir: Base directory for learning data
    """
    due = get_due_reviews(topic_slug, base_dir)

    if not due:
        output = {
            "status": "no_reviews_due",
            "due_count": 0,
            "reviews": [],
            "llm_directive": "No reviews needed. Proceed with new learning or ask user what they'd like to learn.",
            "suggested_response": "✅ Нет запланированных повторений! Готов(а) к новому?"
        }
        print(json.dumps(output, indent=2))
        return

    # Build suggested prompt for LLM
    review_list = "\n".join([
        f"{i+1}. {item['concept']}" + (f" ({item['days_overdue']} дн. просрочено)" if item['days_overdue'] > 0 else " (на сегодня)")
        for i, item in enumerate(due)
    ])

    output = {
        "status": "reviews_due",
        "due_count": len(due),
        "reviews": due,
        "llm_directive": "STOP. Conduct review session BEFORE new learning. Ask user to explain each concept. Mark as reviewed after using 'review_scheduler.py review' command.",
        "suggested_prompt": f"📚 У тебя {len(due)} концепций для повторения! Давай повторим перед новым материалом:\n\n{review_list}\n\nРасскажи о '{due[0]['concept']}' своими словами?"
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add concept:    python3 review_scheduler.py add <topic_slug> <concept>")
        print("  Mark reviewed:  python3 review_scheduler.py review <topic_slug> <concept> [quality 0-5]")
        print("  Show status:    python3 review_scheduler.py status <topic_slug>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add" and len(sys.argv) >= 4:
        add_review_item(sys.argv[2], sys.argv[3])
    elif command == "review" and len(sys.argv) >= 4:
        quality = int(sys.argv[4]) if len(sys.argv) >= 5 else 3
        mark_reviewed(sys.argv[2], sys.argv[3], quality=quality)
    elif command == "status" and len(sys.argv) >= 3:
        show_review_status(sys.argv[2])
    else:
        print("❌ Invalid command or missing arguments")
