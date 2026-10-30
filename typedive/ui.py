"""The curses front end. All it does is draw a GameState and feed keys in.

Nothing in here is tested directly (curses screens are painful to
fake); the rules it draws live in engine.py and are tested there.
"""

from __future__ import annotations

import curses
import time
from dataclasses import dataclass

from .engine import GameState, handle_key, tick
from .words import DEFAULT_WORDS

FRAME_SECONDS = 0.05
# TODO: colour themes are a one-line change here (add a --theme flag
# and a second colour pair) — leaving it for a later evening.


@dataclass
class PlayConfig:
    start_level: int = 1
    words: list[str] | None = None
    seed: int | None = None


def _draw(stdscr: "curses._CursesWindow", state: GameState, paused: bool) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    header = (
        f"Score: {state.score}   Lives: {state.lives}   "
        f"Level: {state.level}   Streak: {state.streak}"
    )
    stdscr.addstr(0, 0, header[: max(0, width - 1)])
    for word in state.active:
        row = int(word.row)
        if row < 1 or row >= height - 1 or word.column >= width:
            continue
        text = word.text[: max(0, width - word.column)]
        if word.typed:
            # Typed part in bold so you can see your progress at a glance.
            stdscr.addstr(row, word.column, text[: word.typed], curses.A_BOLD)
            stdscr.addstr(row, word.column + word.typed, text[word.typed :])
        else:
            stdscr.addstr(row, word.column, text)
    footer = "Type the falling words before they land  |  P pause  |  ESC quit"
    stdscr.addstr(height - 1, 0, footer[: max(0, width - 1)])
    if paused:
        message = "PAUSED - press P to continue"
        stdscr.addstr(height // 2, max(0, (width - len(message)) // 2), message, curses.A_BOLD)
    stdscr.refresh()


def _game_over_screen(stdscr: "curses._CursesWindow", state: GameState) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    lines = [
        "GAME OVER",
        f"Final score: {state.score}",
        f"Words cleared: {state.cleared}   Reached level: {state.level}",
        f"Best streak: {state.best_streak}",
        "",
        "Press any key to exit",
    ]
    for i, line in enumerate(lines):
        row = height // 2 - 3 + i
        if 0 <= row < height:
            stdscr.addstr(row, max(0, (width - len(line)) // 2), line)
    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()


def play(stdscr: "curses._CursesWindow", config: PlayConfig) -> GameState:
    """Run one game inside an already-initialised curses screen."""
    from .engine import new_game

    height, width = stdscr.getmaxyx()
    state = new_game(width, height, config.words or DEFAULT_WORDS,
                     start_level=config.start_level, seed=config.seed)
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    paused = False
    last = time.monotonic()
    while not state.game_over:
        now = time.monotonic()
        dt = now - last
        last = now
        if not paused:
            tick(state, dt)
        _draw(stdscr, state, paused)
        key = stdscr.getch()
        if key == -1:
            time.sleep(FRAME_SECONDS)
            continue
        if key == 27:  # ESC
            break
        if key in (ord("p"), ord("P")):
            paused = not paused
            continue
        if paused or key < 32 or key > 126:
            continue
        handle_key(state, chr(key))
    if state.game_over:
        _game_over_screen(stdscr, state)
    return state


def run(config: PlayConfig) -> GameState:
    """Entry point for the curses wrapper (handles terminal setup/teardown)."""
    return curses.wrapper(play, config)
