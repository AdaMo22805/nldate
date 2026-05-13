import calendar
import re
from datetime import date, timedelta


_MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

_WEEKDAYS = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "tues": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thurs": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}

_MONTH_RE = "|".join(_MONTHS)
_WEEKDAY_RE = "|".join(_WEEKDAYS)

_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

_COUNT_RE = "|".join(["\\d+", "an?", *_NUMBER_WORDS])


def _add_months(d: date, months: int) -> date:
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last_day))


def _resolve_count(raw: str) -> int:
    if raw in ("a", "an"):
        return 1
    if raw in _NUMBER_WORDS:
        return _NUMBER_WORDS[raw]
    return int(raw)


def _add_offset(d: date, n: int, unit: str) -> date:
    if unit.startswith("day"):
        return d + timedelta(days=n)
    if unit.startswith("week"):
        return d + timedelta(weeks=n)
    if unit.startswith("month"):
        return _add_months(d, n)
    return _add_months(d, n * 12)


def parse(s: str, today: date | None = None) -> date:
    """Parse a natural language date expression into a ``datetime.date``.

    Accepts a free-form natural language description of a date (for example,
    ``"tomorrow"``, ``"next Tuesday"``, ``"March 3rd"``, or
    ``"three weeks from now"``) and converts it into a concrete
    ``datetime.date`` object.

    Args:
        s: The natural language date expression to parse.
        today: Reference point used to resolve relative date expressions
            such as ``"tomorrow"`` or ``"next Tuesday"``. If ``None``,
            defaults to the current date.

    Returns:
        The ``datetime.date`` that ``s`` refers to.
    """
    if today is None:
        today = date.today()

    text = s.strip().lower()

    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today - timedelta(days=1)

    if text == "next week":
        return today + timedelta(weeks=1)
    if text == "last week":
        return today - timedelta(weeks=1)
    if text == "this week":
        return today

    if m := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text):
        y, mo, d = map(int, m.groups())
        return date(y, mo, d)

    if m := re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", text):
        y, mo, d = map(int, m.groups())
        return date(y, mo, d)

    if m := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", text):
        mo, d, y = map(int, m.groups())
        if y < 100:
            y += 2000
        return date(y, mo, d)

    if m := re.fullmatch(
        rf"({_MONTH_RE})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(\d{{4}}))?",
        text,
    ):
        mo = _MONTHS[m.group(1)]
        d = int(m.group(2))
        y = int(m.group(3)) if m.group(3) else today.year
        return date(y, mo, d)

    if m := re.fullmatch(
        rf"(?:in\s+)?({_COUNT_RE})\s+(day|days|week|weeks|month|months|year|years)(?:\s+(from\s+now|ago))?",
        text,
    ):
        n = _resolve_count(m.group(1))
        if m.group(3) == "ago":
            n = -n
        return _add_offset(today, n, m.group(2))

    if m := re.fullmatch(
        rf"({_COUNT_RE})\s+(day|days|week|weeks|month|months|year|years)"
        rf"(?:\s+(?:and|&)|,)\s+"
        rf"({_COUNT_RE})\s+(day|days|week|weeks|month|months|year|years)"
        rf"\s+(before|after|since)\s+(.+)",
        text,
    ):
        n1 = _resolve_count(m.group(1))
        n2 = _resolve_count(m.group(3))
        if m.group(5) == "before":
            n1, n2 = -n1, -n2
        anchor = parse(m.group(6), today=today)
        return _add_offset(_add_offset(anchor, n1, m.group(2)), n2, m.group(4))

    if m := re.fullmatch(
        rf"({_COUNT_RE})\s+(day|days|week|weeks|month|months|year|years)\s+(before|after|since)\s+(.+)",
        text,
    ):
        n = _resolve_count(m.group(1))
        if m.group(3) == "before":
            n = -n
        anchor = parse(m.group(4), today=today)
        return _add_offset(anchor, n, m.group(2))

    if m := re.fullmatch(r"the\s+(day|week|month|year)\s+(before|after)\s+(.+)", text):
        anchor = parse(m.group(3), today=today)
        n = -1 if m.group(2) == "before" else 1
        return _add_offset(anchor, n, m.group(1))

    if m := re.fullmatch(
        rf"({_COUNT_RE})\s+({_WEEKDAY_RE})s?\s+(from\s+now|ago)",
        text,
    ):
        n = _resolve_count(m.group(1))
        target = _WEEKDAYS[m.group(2)]
        current = today.weekday()
        if m.group(3) == "from now":
            days = (target - current) % 7 or 7
            return today + timedelta(days=days + 7 * (n - 1))
        days = (current - target) % 7 or 7
        return today - timedelta(days=days + 7 * (n - 1))

    if m := re.fullmatch(rf"(next|last|this)\s+({_WEEKDAY_RE})", text):
        modifier = m.group(1)
        target = _WEEKDAYS[m.group(2)]
        current = today.weekday()
        if modifier == "this":
            return today + timedelta(days=target - current)
        if modifier == "next":
            days_ahead = (target - current) % 7 or 7
            return today + timedelta(days=days_ahead)
        days_back = (current - target) % 7 or 7
        return today - timedelta(days=days_back)

    if m := re.fullmatch(rf"({_WEEKDAY_RE})", text):
        target = _WEEKDAYS[m.group(1)]
        days_ahead = (target - today.weekday()) % 7 or 7
        return today + timedelta(days=days_ahead)

    raise ValueError(f"Could not parse date expression: {s!r}")


def hello() -> str:
    return "Hello from nldate!"
