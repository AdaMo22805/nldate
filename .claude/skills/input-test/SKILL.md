---
name: input-test
description: Add support for a new natural-language date input to the nldate parser on a dedicated feature branch. Writes a failing test, extends parse() to handle it, verifies the full test suite passes, then commits and squash-merges into main.
---

# input-test

Invoked as `/input-test <input-string>` (the argument is the natural-language date expression to support, e.g. `"the day after tomorrow"` or `"end of next month"`).

## Workflow

1. **Branch from current `main`.** Pick a short kebab-case slug derived from the input (2–4 words, e.g. `"3 days ago"` → `days-ago`; `"end of next month"` → `end-of-month`). Then:
   ```
   git checkout main
   git checkout -b dev-input-<slug>
   ```
   Always branch from `main` HEAD — never reuse a stale feature branch, since prior squash-merges produced new SHAs and reusing old branches causes false merge conflicts.

2. **Confirm the expected output.** Ask the user what `parse(<input>)` should return as a `datetime.date`. For relative expressions, confirm which reference date (`today=...`) to pin against — the existing suite uses `REFERENCE = date(2026, 5, 13)` (a Wednesday). If the answer is unambiguous, state the assumption inline and proceed without blocking.

3. **Add a failing test** in `tests/test_parse.py`. Place it in the most appropriate existing class (`TestAbsoluteDates`, `TestRelativeDates`, `TestWeekdays`, `TestAbbreviations`, `TestCaseInsensitive`, `TestWhitespace`, `TestSingularUnits`, `TestMonthWithoutYear`, `TestYearBoundaries`, `TestSameWeekday`, `TestInvalidInputs`, `TestReturnType`) — or add a new class if none fit. Reuse `REFERENCE` for relative inputs.

4. **Confirm the test fails**: `uv run pytest -v tests/test_parse.py::<class>::<test>`.

5. **Extend `parse()`** in `src/nldate/__init__.py` to handle the new pattern. Prefer minimal additions:
   - Literal keyword? Add a `text == "..."` check near the top.
   - New regex pattern? Add a `re.fullmatch` branch alongside the existing ones.
   - Month/year arithmetic? Reuse `_add_months(d, months)` (years = `n * 12` months).
   - Case differences are already handled by `text = s.strip().lower()` at the top of `parse()`.

6. **Verify everything passes**:
   ```
   uv run ruff format src tests
   uv run ruff check src tests
   uv run mypy src tests
   uv run pytest -q
   ```
   All four must succeed before continuing.

7. **Commit on the feature branch.** Stage `src/nldate/__init__.py` and `tests/test_parse.py` only (no `__pycache__`). Use a concise message summarizing the input now supported and the change to `parse()`. Include the standard `Co-Authored-By` trailer.

8. **Squash-merge into `main`.**
   ```
   git checkout main
   git merge --squash dev-input-<slug>
   git commit -m "<same message as step 7>"
   ```
   This should fast-forward cleanly because the branch was cut from current `main`.

9. **Offer cleanup.** Tell the user the branch can be deleted (`git branch -D dev-input-<slug>`) and that `origin/main` is now behind. Do **not** push or delete without explicit authorization.

10. **Report**: the branch name and slug, new test name(s), the regex/branch added to `parse()`, the final passing test count, and the new `main` commit SHA.
