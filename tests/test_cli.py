"""Tests for the CLI surface: flags, scores listing, bad input."""

from typedive.cli import main
from typedive.scores import save_score


def test_scores_flag_with_no_scores(tmp_path, capsys):
    assert main(["--scores", "--score-file", str(tmp_path / "scores.json")]) == 0
    assert "No scores yet" in capsys.readouterr().out


def test_scores_flag_lists_saved_scores(tmp_path, capsys):
    path = tmp_path / "scores.json"
    save_score(path, 120, 3)
    assert main(["--scores", "--score-file", str(path)]) == 0
    assert "120" in capsys.readouterr().out


def test_bad_level_is_usage_error_not_traceback(capsys):
    assert main(["--level", "0"]) == 2
    assert "error:" in capsys.readouterr().err


def test_missing_words_file_is_usage_error_not_traceback(capsys):
    assert main(["--words-file", "/tmp/typedive-test-nope.txt"]) == 2
    assert "not found" in capsys.readouterr().err
