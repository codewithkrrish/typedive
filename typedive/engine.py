"""The game itself, with no terminal code in it.

Keeping the rules here (and the drawing in ui.py) means the whole game
can be tested without opening a curses screen, which is the only sane
way I found to test a terminal game.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

# Tunables, kept in one place so tweaking the difficulty is one edit.
MAX_LIVES = 3
WORDS_PER_LEVEL = 8
MIN_TERMINAL_WIDTH = 30
MIN_TERMINAL_HEIGHT = 12
BASE_SPEED = 1.2  # rows per second at level 1
SPEED_PER_LEVEL = 0.7
MAX_SPEED = 8.0
BASE_SPAWN_INTERVAL = 2.4  # seconds between spawns at level 1
SPAWN_SHRINK_PER_LEVEL = 0.15
MIN_SPAWN_INTERVAL = 0.9
POINTS_PER_LETTER = 10
STREAK_BONUS_PER_WORD = 5


@dataclass
class FallingWord:
    """One word currently on screen."""

    text: str
    column: int
    row: float
    typed: int = 0

    @property
    def next_char(self) -> str | None:
        """The next letter the player has to type, or None if done."""
        if self.typed >= len(self.text):
            return None
        return self.text[self.typed]

    @property
    def is_complete(self) -> bool:
        return self.typed >= len(self.text)


@dataclass
class KeyResult:
    matched: bool
    completed_word: str | None = None
    points: int = 0


@dataclass
class GameState:
    width: int
    height: int
    words: list[str]
    rng: random.Random = field(default_factory=random.Random)
    score: int = 0
    lives: int = MAX_LIVES
    level: int = 1
    streak: int = 0
    best_streak: int = 0
    cleared: int = 0
    active: list[FallingWord] = field(default_factory=list)
    game_over: bool = False
    _spawn_timer: float = 0.0

    @property
    def bottom_row(self) -> int:
        """Row a word must not reach (the line above the footer)."""
        return self.height - 2


def speed_for_level(level: int) -> float:
    """Fall speed in rows per second. Grows with level, capped."""
    return min(MAX_SPEED, BASE_SPEED + SPEED_PER_LEVEL * (level - 1))


def spawn_interval_for_level(level: int) -> float:
    """Seconds between spawns. Shrinks with level, floored."""
    return max(
        MIN_SPAWN_INTERVAL,
        BASE_SPAWN_INTERVAL - SPAWN_SHRINK_PER_LEVEL * (level - 1),
    )


def new_game(
    width: int,
    height: int,
    words: list[str],
    start_level: int = 1,
    seed: int | None = None,
) -> GameState:
    """Create a fresh game, validating the bits that would break the UI.

    Raises ValueError with a plain message for bad sizes, an empty word
    list, or a start level below 1, so the CLI can print it as-is.
    """
    if width < MIN_TERMINAL_WIDTH or height < MIN_TERMINAL_HEIGHT:
        raise ValueError(
            f"terminal too small: need at least "
            f"{MIN_TERMINAL_WIDTH}x{MIN_TERMINAL_HEIGHT}, "
            f"got {width}x{height}"
        )
    if not words:
        raise ValueError("word list is empty, nothing to fall")
    if start_level < 1:
        raise ValueError("start level must be 1 or higher")
    state = GameState(
        width=width,
        height=height,
        words=list(words),
        rng=random.Random(seed),
        level=start_level,
    )
    spawn_word(state)
    return state


def spawn_word(state: GameState) -> FallingWord:
    """Drop a new word at the top of the screen.

    Avoids repeating a word that is already falling when there is any
    choice, so the screen does not fill with the same word twice.
    """
    on_screen = {word.text for word in state.active}
    choices = [w for w in state.words if w not in on_screen] or state.words
    text = state.rng.choice(choices)
    max_column = max(0, state.width - len(text) - 1)
    word = FallingWord(text=text, column=state.rng.randint(0, max_column), row=1.0)
    state.active.append(word)
    return word


def handle_key(state: GameState, char: str) -> KeyResult:
    """Feed one typed character into the game.

    The character lands on the word closest to the bottom whose next
    letter matches. A character matching nothing breaks the streak;
    it does not cost a life (losing a life is only for words that land).
    """
    if state.game_over or len(char) != 1:
        return KeyResult(matched=False)
    candidates = [w for w in state.active if w.next_char == char]
    if not candidates:
        state.streak = 0
        return KeyResult(matched=False)
    # Closest to the bottom first: that word is the urgent one.
    target = max(candidates, key=lambda w: w.row)
    target.typed += 1
    if not target.is_complete:
        return KeyResult(matched=True)
    state.active.remove(target)
    points = len(target.text) * POINTS_PER_LETTER + state.streak * STREAK_BONUS_PER_WORD
    state.score += points
    state.streak += 1
    state.best_streak = max(state.best_streak, state.streak)
    state.cleared += 1
    if state.cleared % WORDS_PER_LEVEL == 0:
        state.level += 1
    return KeyResult(matched=True, completed_word=target.text, points=points)


def tick(state: GameState, dt_seconds: float) -> list[str]:
    """Advance the game by dt_seconds. Returns words that hit the floor.

    Each landed word costs one life and breaks the streak. When lives
    run out the game is over; the UI reads state.game_over.
    """
    if state.game_over or dt_seconds <= 0:
        return []
    speed = speed_for_level(state.level)
    for word in state.active:
        word.row += speed * dt_seconds
    landed = [w for w in state.active if int(w.row) >= state.bottom_row]
    for word in landed:
        state.active.remove(word)
        state.lives -= 1
        state.streak = 0
    if state.lives <= 0:
        state.lives = 0
        state.game_over = True
    state._spawn_timer -= dt_seconds
    if state._spawn_timer <= 0 and not state.game_over:
        spawn_word(state)
        state._spawn_timer = spawn_interval_for_level(state.level)
    return [w.text for w in landed]
