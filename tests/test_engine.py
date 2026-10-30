"""Tests for the game rules. No curses involved, by design."""

import random

import pytest

from typedive.engine import (
    handle_key,
    new_game,
    spawn_interval_for_level,
    spawn_word,
    speed_for_level,
    tick,
)


def make_game(words=("apple", "river", "cloud"), level=1, seed=7):
    return new_game(80, 24, list(words), start_level=level, seed=seed)


def test_new_game_rejects_tiny_terminal():
    with pytest.raises(ValueError, match="terminal too small"):
        new_game(20, 10, ["apple"])


def test_new_game_rejects_empty_word_list():
    with pytest.raises(ValueError, match="empty"):
        new_game(80, 24, [])


def test_new_game_rejects_bad_level():
    with pytest.raises(ValueError, match="level"):
        new_game(80, 24, ["apple"], start_level=0)


def test_typing_a_word_scores_and_clears_it():
    state = make_game()
    state.active = []
    word = spawn_word(state)
    for char in word.text:
        result = handle_key(state, char)
    assert result.matched
    assert result.completed_word == word.text
    assert word not in state.active
    assert state.score == len(word.text) * 10
    assert state.cleared == 1


def test_wrong_key_breaks_streak_but_not_score():
    state = make_game()
    state.active = []
    first = spawn_word(state)
    for char in first.text:
        handle_key(state, char)
    assert state.streak == 1
    score_before = state.score
    second = spawn_word(state)
    wrong = "z" if second.text[0] != "z" else "q"
    assert handle_key(state, wrong).matched is False
    assert state.streak == 0
    assert state.score == score_before


def test_key_goes_to_word_closest_to_bottom():
    state = make_game()
    from typedive.engine import FallingWord

    state.active = [
        FallingWord(text="apple", column=0, row=2.0),
        FallingWord(text="amber", column=10, row=10.0),
    ]
    handle_key(state, "a")
    assert state.active[1].typed == 1  # the lower word got the letter
    assert state.active[0].typed == 0


def test_word_hitting_floor_costs_a_life():
    state = make_game()
    from typedive.engine import FallingWord

    state.active = [FallingWord(text="apple", column=0, row=21.0)]
    state._spawn_timer = 999  # keep the spawn out of this test
    landed = tick(state, 1.0)
    assert landed == ["apple"]
    assert state.lives == 2
    assert state.game_over is False


def test_losing_last_life_ends_game():
    state = make_game()
    from typedive.engine import FallingWord

    state.lives = 1
    state.active = [FallingWord(text="apple", column=0, row=21.0)]
    state._spawn_timer = 999
    tick(state, 1.0)
    assert state.game_over is True
    assert state.lives == 0


def test_level_rises_after_eight_clears():
    state = make_game()
    state.active = []
    for _ in range(8):
        word = spawn_word(state)
        for char in word.text:
            handle_key(state, char)
    assert state.cleared == 8
    assert state.level == 2
    assert speed_for_level(2) > speed_for_level(1)
    assert spawn_interval_for_level(2) < spawn_interval_for_level(1)


def test_speed_is_capped():
    assert speed_for_level(99) == 8.0


def test_spawn_avoids_duplicate_on_screen_word():
    state = make_game(words=("apple", "river"))
    state.active = []
    first = spawn_word(state)
    second = spawn_word(state)
    assert second.text != first.text


def test_tick_with_no_time_changes_nothing():
    state = make_game()
    before = [(w.text, w.row) for w in state.active]
    assert tick(state, 0) == []
    assert [(w.text, w.row) for w in state.active] == before


def test_seeded_game_is_reproducible():
    first = make_game(seed=42)
    second = make_game(seed=42)
    assert [w.text for w in first.active] == [w.text for w in second.active]
    assert first.active[0].column == second.active[0].column
