"""Command line: parse flags, then hand off to the game. Nothing else.

Every error path here prints a plain sentence on stderr and returns
an exit code, because a player who mistyped a flag should not get a
traceback for their trouble.
"""

from __future__ import annotations

import argparse
import sys

from .scores import default_score_file, load_scores, save_score
from .ui import PlayConfig, run
from .words import DEFAULT_WORDS, WordListError, load_words

EXIT_OK = 0
EXIT_USAGE = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="typedive",
        description="Falling-word typing game for your terminal.",
    )
    parser.add_argument("--level", type=int, default=1,
                        help="starting level (1 or higher, default: 1)")
    parser.add_argument("--words-file", metavar="FILE",
                        help="custom word list, one word per line")
    parser.add_argument("--score-file", metavar="FILE",
                        help="where to keep high scores "
                             "(default: ~/.typedive-scores.json)")
    parser.add_argument("--seed", type=int, default=None,
                        help="fixed random seed, for practice runs")
    parser.add_argument("--scores", action="store_true",
                        help="print the high score table and exit")
    return parser


def print_scores(score_file: str | None) -> int:
    path = score_file or str(default_score_file())
    entries = load_scores(path)
    if not entries:
        print("No scores yet. Play a game first: typedive")
        return EXIT_OK
    print("High scores:")
    for rank, entry in enumerate(entries, start=1):
        print(f"{rank}. {entry.score} points (level {entry.level}, {entry.day})")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.scores:
        return print_scores(args.score_file)
    if args.level < 1:
        print("error: --level must be 1 or higher", file=sys.stderr)
        return EXIT_USAGE
    try:
        words = load_words(args.words_file) if args.words_file else DEFAULT_WORDS
    except WordListError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    score_path = args.score_file or str(default_score_file())
    try:
        state = run(PlayConfig(start_level=args.level, words=words, seed=args.seed))
    except Exception as exc:  # curses errors, tiny terminals, Ctrl-C
        print(f"error: could not start the game: {exc}", file=sys.stderr)
        return EXIT_USAGE
    if state.score > 0:
        entries = save_score(score_path, state.score, state.level)
        best = entries[0].score if entries else state.score
        print(f"\nScore: {state.score}  (best: {best})")
        print(f"Words cleared: {state.cleared}  Reached level: {state.level}")
    else:
        print("\nNo score this time. Run it again: typedive")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
