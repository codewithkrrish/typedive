"""Tests for high scores and custom word lists."""

import json

import pytest

from typedive.scores import load_scores, save_score
from typedive.words import WordListError, load_words


def test_missing_score_file_means_no_scores(tmp_path):
    assert load_scores(tmp_path / "scores.json") == []


def test_corrupt_score_file_means_no_scores(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text("{not json", encoding="utf-8")
    assert load_scores(path) == []


def test_corrupt_rows_are_skipped_not_fatal(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text(
        json.dumps([
            {"score": 100, "level": 2, "day": "2026-10-30"},
            {"score": "oops"},
            "junk",
        ]),
        encoding="utf-8",
    )
    entries = load_scores(path)
    assert len(entries) == 1 and entries[0].score == 100


def test_save_keeps_top_ten_sorted(tmp_path):
    path = tmp_path / "scores.json"
    for score in range(10, 130, 10):
        save_score(path, score, 1)
    save_score(path, 999, 5)
    entries = load_scores(path)
    assert len(entries) == 10
    assert entries[0].score == 999
    assert [e.score for e in entries] == sorted((e.score for e in entries), reverse=True)


def test_save_is_atomic_and_readable_afterwards(tmp_path):
    path = tmp_path / "scores.json"
    save_score(path, 50, 1)
    assert json.loads(path.read_text(encoding="utf-8"))[0]["score"] == 50


def test_load_words_skips_blanks_and_bad_lines(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("Apple\n\nriver2\n  cloud  \n", encoding="utf-8")
    assert load_words(path) == ["apple", "cloud"]


def test_load_words_missing_file(tmp_path):
    with pytest.raises(WordListError, match="not found"):
        load_words(tmp_path / "nope.txt")


def test_load_words_empty_file(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("\n\n", encoding="utf-8")
    with pytest.raises(WordListError, match="no usable words"):
        load_words(path)
