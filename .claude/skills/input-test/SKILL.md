---
name: input-test
description: Add support for a new natural-language date input to the nldate parser. Takes the input string as an argument, writes a failing test, extends parse() to handle it, and verifies the full test suite still passes.
---

# input-test

Invoked as `/input-test <input-string>` (the argument is the natural-language date expression to support, e.g. `"the day after tomorrow"` or `"end of next month"`).

## Workflow

1. **Confirm the expected output.** Ask the user what `parse(<input>)` should return as a `datetime.date`. For relative expressions, confirm which reference date (`today=...`) the test should pin against — the existing suite uses `REFERENCE = date(2026, 5, 13)` (a Wednesday).

2. **Add a failing test** in `tests/test_parse.py`. Place it in the most appropriate existing class (`TestAbsoluteDates`, `TestRelativeDates`, `TestWeekdays`, `TestAbbreviations`, `TestCaseInsensitive`, `TestWhitespace`, `TestSingularUnits`, `TestMonthWithoutYear`, `TestYearBoundaries`, `TestSameWeekday`, `TestInvalidInputs`, `TestReturnType`) — or add a new class if none fit. Reuse `REFERENCE` for relative inputs.

3. **Confirm the test fails**: `uv run pytest -v tests/test_parse.py::<class>::<test>`.

4. **Extend `parse()`** in `src/nldate/__init__.py` to handle the new pattern. Prefer minimal additions:
   - Literal keyword? Add a `text == "..."` check near the top.
   - New regex pattern? Add a `re.fullmatch` branch alongside the existing ones.
   - Month arithmetic? Reuse `_add_months(d, months)`.
   - Case differences are already handled by `text = s.strip().lower()` at the top of `parse()`.

5. **Verify everything passes**:
   ```
   uv run ruff format src tests
   uv run ruff check src tests
   uv run mypy src tests
   uv run pytest -q
   ```
   All four must succeed before reporting done.

6. **Report**: the new test name(s), the regex/branch added to `parse()`, and the final passing test count.
