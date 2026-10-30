"""High scores: a small JSON file, written atomically.

The file is allowed to be missing or even corrupt (a half-written file
from a killed run, say) — both just mean "no scores yet". It is never
allowed to take the game down with it.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

MAX_ENTRIES = 10


@dataclass
class ScoreEntry:
    score: int
    level: int
    day: str  # YYYY-MM-DD


def default_score_file() -> Path:
    return Path.home() / ".typedive-scores.json"


def load_scores(path: str | Path) -> list[ScoreEntry]:
    """Read the score file, tolerating a missing or broken file."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return []
    if not isinstance(raw, list):
        return []
    entries = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            entries.append(
                ScoreEntry(
                    score=int(item["score"]),
                    level=int(item["level"]),
                    day=str(item["day"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue  # one bad row must not poison the whole table
    entries.sort(key=lambda entry: entry.score, reverse=True)
    return entries[:MAX_ENTRIES]


def save_score(path: str | Path, score: int, level: int) -> list[ScoreEntry]:
    """Insert a score, keep the top 10, and write atomically.

    The write goes to a temp file in the same directory followed by a
    rename, so a crash mid-write leaves either the old file or the new
    one, never a half-written file.
    """
    file_path = Path(path)
    entries = load_scores(file_path)
    entries.append(ScoreEntry(score=score, level=level, day=date.today().isoformat()))
    entries.sort(key=lambda entry: entry.score, reverse=True)
    entries = entries[:MAX_ENTRIES]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        [{"score": e.score, "level": e.level, "day": e.day} for e in entries],
        indent=2,
    )
    fd, temp_name = tempfile.mkstemp(dir=file_path.parent, prefix=".typedive-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temp_name, file_path)
    except BaseException:
        # Best effort cleanup; the original file is untouched either way.
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
    return entries
