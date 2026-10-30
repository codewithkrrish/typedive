"""Word lists: the built-in set, plus loading a custom one from a file."""

from __future__ import annotations

from pathlib import Path

# Short everyday words. I kept them 3-8 letters: shorter than that and
# the game is just mashing, longer and level 1 feels unfair.
DEFAULT_WORDS = [
    "apple", "river", "cloud", "brick", "storm", "light", "music",
    "paper", "stone", "flame", "ocean", "wind", "leaf", "star",
    "moon", "road", "king", "wolf", "bear", "fish", "song",
    "book", "door", "rain", "snow", "fire", "gold", "iron",
    "ship", "tree", "sand", "cake", "jump", "run", "play",
    "code", "byte", "disk", "chip", "wire", "node", "loop",
    "data", "pixel", "screen", "mouse", "keyboard", "server",
    "python", "typing", "speed", "quick", "brave", "calm",
    "happy", "jolly", "amber", "coral", "pearl", "ivory",
    "maple", "cedar", "falcon", "tiger", "eagle", "cobra",
    "harbor", "meadow", "canyon", "desert", "island", "valley",
    "garden", "market", "bridge", "tower", "castle", "village",
    "winter", "summer", "autumn", "spring", "morning", "evening",
    "thunder", "breeze", "shadow", "sunset", "sunrise", "midnight",
    "rocket", "planet", "comet", "galaxy", "nebula", "orbit",
    "guitar", "piano", "violin", "drum", "flute", "banjo",
    "puzzle", "riddle", "quest", "magic", "dragon", "wizard",
    "knight", "archer", "shield", "sword", "arrow", "helmet",
    "coffee", "honey", "lemon", "mango", "peach", "berry",
    "cheese", "bread", "butter", "sugar", "spice", "herb",
]


class WordListError(ValueError):
    """Raised when a custom word file cannot be used."""


def load_words(path: str | Path) -> list[str]:
    """Load one word per line from a file.

    Blank lines are skipped, words are lowercased, and anything that is
    not plain letters is ignored rather than crashing the game. If
    nothing usable survives, that is an error, not an empty game.
    """
    file_path = Path(path)
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise WordListError(f"word list not found: {file_path}") from None
    except OSError as exc:
        raise WordListError(f"cannot read word list {file_path}: {exc}") from None
    words = sorted({line.strip().lower() for line in lines if line.strip().isalpha()})
    if not words:
        raise WordListError(f"word list has no usable words: {file_path}")
    return words
