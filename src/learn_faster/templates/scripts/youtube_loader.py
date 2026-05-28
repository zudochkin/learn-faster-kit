#!/usr/bin/env python3
"""
YouTube transcript loader for the `reading` mode.

Wraps yt-dlp to:
  - probe a video (duration, chapters, available subtitle languages)
  - fetch a transcript (.vtt) and parse it into a normalized JSON index
  - slice the transcript by chapter time range for the Active Reading Loop

Exit codes:
  0 - success
  1 - network / parse / usage error
  2 - yt-dlp not installed (not on PATH)
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SUB_LANG_DEFAULT = ["ru", "en"]
VTT_CUE_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})[^\n]*\n(.+?)(?=\n\n|\Z)",
    re.DOTALL,
)
VTT_STYLE_TAG_RE = re.compile(r"<c[^>]*>|</c>|<\d{2}:\d{2}:\d{2}\.\d{3}>")
TIMECODE_LINE_RE = re.compile(r"^(\d+):(\d+)(?::(\d+))?\s+(.+)$")


def err(msg: str, code: int = 1) -> None:
    print(json.dumps({"status": "error", "error": msg}), file=sys.stdout)
    sys.exit(code)


def require_yt_dlp() -> None:
    if shutil.which("yt-dlp") is None:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": "yt-dlp не найден в PATH",
                    "install": [
                        "brew install yt-dlp",
                        "uv tool install yt-dlp",
                        "pipx install yt-dlp",
                    ],
                }
            )
        )
        sys.exit(2)


def parse_vtt_timestamp_to_seconds(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_vtt(vtt_text: str) -> list[dict[str, Any]]:
    cues: list[dict[str, Any]] = []
    last_text: str | None = None
    for match in VTT_CUE_RE.finditer(vtt_text):
        h1, m1, s1, ms1, h2, m2, s2, ms2, raw = match.groups()
        start = parse_vtt_timestamp_to_seconds(h1, m1, s1, ms1)
        end = parse_vtt_timestamp_to_seconds(h2, m2, s2, ms2)
        text = VTT_STYLE_TAG_RE.sub("", raw)
        text = re.sub(r"\s+", " ", text).strip()
        if not text or text == last_text:
            continue
        cues.append({"start": start, "end": end, "text": text})
        last_text = text
    return cues


def run_yt_dlp_json(url: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["yt-dlp", "--skip-download", "--dump-json", "--no-warnings", url],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        err(f"yt-dlp --dump-json failed: {proc.stderr.strip()[:500]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        err(f"yt-dlp вернул невалидный JSON: {e}")
    return {}  # unreachable


def cmd_probe(args: argparse.Namespace) -> None:
    require_yt_dlp()
    info = run_yt_dlp_json(args.url)

    chapters_raw = info.get("chapters") or []
    chapters = [
        {
            "start_time": float(c.get("start_time", 0.0)),
            "end_time": float(c.get("end_time", 0.0)),
            "title": str(c.get("title", "")).strip() or f"Chapter {i+1}",
        }
        for i, c in enumerate(chapters_raw)
    ]

    manual_subs = list((info.get("subtitles") or {}).keys())
    auto_subs = list((info.get("automatic_captions") or {}).keys())

    print(
        json.dumps(
            {
                "status": "ok",
                "video_id": info.get("id"),
                "title": info.get("title"),
                "duration": float(info.get("duration", 0.0)),
                "has_chapters": len(chapters) >= 2,
                "chapters": chapters,
                "available_subtitle_langs": {
                    "manual": manual_subs,
                    "auto": auto_subs,
                },
                "webpage_url": info.get("webpage_url"),
            },
            ensure_ascii=False,
        )
    )


def _pick_lang(prefs: list[str], available: list[str]) -> str | None:
    avail_set = set(available)
    for p in prefs:
        if p in avail_set:
            return p
    for p in prefs:
        for a in available:
            if a.startswith(p + "-") or a == p + "-orig":
                return a
    return available[0] if available else None


def cmd_fetch(args: argparse.Namespace) -> None:
    require_yt_dlp()
    topic_dir = Path(".learning") / args.topic_slug
    if not topic_dir.exists():
        err(f"тема не найдена: {topic_dir}")

    langs = [lng.strip() for lng in args.lang.split(",") if lng.strip()]
    info = run_yt_dlp_json(args.url)
    duration = float(info.get("duration", 0.0))

    manual_avail = list((info.get("subtitles") or {}).keys())
    auto_avail = list((info.get("automatic_captions") or {}).keys())

    chosen_lang = _pick_lang(langs, manual_avail)
    transcript_source = "user" if chosen_lang else None
    if not chosen_lang:
        chosen_lang = _pick_lang(langs, auto_avail)
        if chosen_lang:
            transcript_source = "auto"

    if not chosen_lang:
        print(
            json.dumps(
                {
                    "status": "no_transcript",
                    "duration": duration,
                    "transcript_source": "none",
                    "title": info.get("title"),
                    "video_id": info.get("id"),
                },
                ensure_ascii=False,
            )
        )
        return

    out_template = str(topic_dir / "transcript.%(ext)s")
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--sub-format",
        "vtt",
        "--sub-lang",
        chosen_lang,
        "--output",
        out_template,
        "--no-warnings",
    ]
    if transcript_source == "user":
        cmd.append("--write-sub")
    else:
        cmd.append("--write-auto-sub")
    cmd.append(args.url)

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        err(f"yt-dlp subtitle download failed: {proc.stderr.strip()[:500]}")

    candidates = sorted(glob.glob(str(topic_dir / "transcript*.vtt")))
    if not candidates:
        err("yt-dlp не создал .vtt файл")
    vtt_path = Path(candidates[-1])
    canonical_vtt = topic_dir / "transcript.vtt"
    if vtt_path != canonical_vtt:
        if canonical_vtt.exists():
            canonical_vtt.unlink()
        vtt_path.rename(canonical_vtt)
        for extra in candidates[:-1]:
            try:
                Path(extra).unlink()
            except OSError:
                pass

    vtt_text = canonical_vtt.read_text(encoding="utf-8", errors="replace")
    cues = parse_vtt(vtt_text)
    if not cues:
        err("парсер VTT не нашёл cues")

    transcript_json = topic_dir / "transcript.json"
    transcript_json.write_text(
        json.dumps({"cues": cues, "lang": chosen_lang, "source": transcript_source}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "transcript_source": transcript_source,
                "lang_used": chosen_lang,
                "num_cues": len(cues),
                "duration": duration,
                "transcript_path": str(transcript_json),
                "vtt_path": str(canonical_vtt),
                "title": info.get("title"),
                "video_id": info.get("id"),
            },
            ensure_ascii=False,
        )
    )


def cmd_slice(args: argparse.Namespace) -> None:
    topic_dir = Path(".learning") / args.topic_slug
    metadata_path = topic_dir / "metadata.json"
    transcript_path = topic_dir / "transcript.json"

    if not metadata_path.exists():
        err(f"metadata.json не найден: {metadata_path}")
    if not transcript_path.exists():
        err(f"transcript.json не найден: {transcript_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    ranges = metadata.get("chapter_ranges") or []
    n = args.chapter
    chapter = next((c for c in ranges if int(c.get("n", -1)) == n), None)
    if chapter is None:
        err(f"глава {n} не найдена в chapter_ranges")

    if "time_start" not in chapter or "time_end" not in chapter:
        err(f"глава {n} не имеет time_start/time_end — не YouTube источник?")

    time_start = float(chapter["time_start"])
    time_end = float(chapter["time_end"])

    payload = json.loads(transcript_path.read_text(encoding="utf-8"))
    cues = payload.get("cues") or []
    chunk = [c["text"] for c in cues if c["end"] > time_start and c["start"] < time_end]
    text = " ".join(chunk).strip()

    print(
        json.dumps(
            {
                "status": "ok",
                "chapter": {
                    "n": n,
                    "title": chapter.get("title"),
                    "time_start": time_start,
                    "time_end": time_end,
                },
                "text": text,
                "num_cues": len(chunk),
            },
            ensure_ascii=False,
        )
    )


def cmd_parse_toc(args: argparse.Namespace) -> None:
    """Parse pasted manual TOC (mm:ss Title lines) into chapter_ranges-like list.

    Reads from stdin. duration is required to fill last chapter's time_end.
    """
    duration = float(args.duration)
    chapters: list[dict[str, Any]] = []
    for line in sys.stdin.read().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = TIMECODE_LINE_RE.match(line)
        if not m:
            continue
        a, b, c, title = m.groups()
        if c is None:
            total = int(a) * 60 + int(b)
        else:
            total = int(a) * 3600 + int(b) * 60 + int(c)
        chapters.append({"start_time": float(total), "title": title.strip()})

    if not chapters:
        err("не нашёл ни одной строки формата `mm:ss Title` или `hh:mm:ss Title`")

    chapter_ranges: list[dict[str, Any]] = []
    for i, ch in enumerate(chapters):
        end = chapters[i + 1]["start_time"] if i + 1 < len(chapters) else duration
        chapter_ranges.append(
            {
                "n": i + 1,
                "title": ch["title"],
                "time_start": ch["start_time"],
                "time_end": end,
            }
        )

    print(json.dumps({"status": "ok", "chapter_ranges": chapter_ranges}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(prog="youtube_loader")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_probe = sub.add_parser("probe", help="metadata + chapters + available subtitle langs")
    p_probe.add_argument("url")
    p_probe.set_defaults(func=cmd_probe)

    p_fetch = sub.add_parser("fetch", help="download subtitles → transcript.vtt + transcript.json")
    p_fetch.add_argument("url")
    p_fetch.add_argument("topic_slug")
    p_fetch.add_argument("--lang", default=",".join(SUB_LANG_DEFAULT))
    p_fetch.set_defaults(func=cmd_fetch)

    p_slice = sub.add_parser("slice", help="extract transcript chunk for chapter N")
    p_slice.add_argument("topic_slug")
    p_slice.add_argument("chapter", type=int)
    p_slice.set_defaults(func=cmd_slice)

    p_parse_toc = sub.add_parser("parse_toc", help="parse manual mm:ss TOC from stdin")
    p_parse_toc.add_argument("duration", help="video duration in seconds (from probe)")
    p_parse_toc.set_defaults(func=cmd_parse_toc)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
