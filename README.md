# typedive

A falling-word typing game that runs in your terminal. Words drop from
the top of the screen, you type them before they hit the floor, and the
game gets faster every level. No account, no window, no dependencies
beyond the Python standard library.

I built this because every typing trainer I tried felt like homework.
I wanted the practice part (faster, more accurate typing) wrapped in
something I would actually open for fun — an arcade loop, three lives,
and a score table to beat next time.

## How it plays

```
Score: 240   Lives: 3   Level: 2   Streak: 4
------------------------------------------------
        river
              cloud
    apple
------------------------------------------------
Type the falling words before they land  |  P pause  |  ESC quit
```

- Type a letter and it lands on the word closest to the floor that
  needs that letter next. You do not have to click or select a word.
- Finish a word to score: 10 points per letter, plus a streak bonus
  for clearing words back to back.
- A word that reaches the floor costs one life and breaks your streak.
  A mistyped letter only breaks your streak — it never costs a life.
- Every 8 cleared words you level up: words fall faster and spawn
  more often. Lose all 3 lives and it is game over.

## Install

You need Python 3.10 or newer.

```bash
pip install git+https://github.com/codewithkrrish/typedive.git
typedive
```

Or run it straight from a clone, no install step:

```bash
git clone https://github.com/codewithkrrish/typedive.git
cd typedive
python -m typedive
```

## Options

```bash
typedive --level 3                 # start harder, skip the warm-up
typedive --words-file words.txt    # your own list, one word per line
typedive --seed 42                 # same spawns every run, for practice
typedive --scores                  # print the high score table and exit
```

Scores live in `~/.typedive-scores.json` by default
(`--score-file` moves them). The table keeps your top 10.

## How it is put together

The rules and the screen are deliberately separate, so the game can
be tested without a terminal:

```
typedive/
  engine.py   fall speed, scoring, lives, levels, streaks (pure logic)
  ui.py       curses drawing and the input loop
  words.py    the built-in word list and custom list loading
  scores.py   the high score file (atomic writes, corrupt-file safe)
  cli.py      flags and plain-English error messages
tests/
  test_engine.py  test_scores_words.py  test_cli.py
```

Run the tests with:

```bash
pip install pytest
python -m pytest
```

## Limitations, honestly

- Terminal only, and only where Python's `curses` module exists —
  that means Linux and macOS. On Windows it will not start, and the
  error message says so instead of crashing.
- The built-in word list is about 120 everyday words, so after a few
  long sessions you will start recognising them. Bring your own list
  with `--words-file` if you want harder or themed words.
- There is no mouse support, no sound, and no multiplayer. It is a
  small arcade game, and I kept it that way on purpose.

## License

MIT — see [LICENSE](LICENSE).

Built by [Krrish](https://github.com/codewithkrrish).
