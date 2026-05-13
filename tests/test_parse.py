from datetime import date

import pytest

from nldate import parse


REFERENCE = date(2026, 5, 13)  # a Wednesday


class TestAbsoluteDates:
    def test_iso_format(self):
        assert parse("2026-03-03") == date(2026, 3, 3)

    def test_month_name_with_year(self):
        assert parse("March 3, 2026") == date(2026, 3, 3)

    def test_month_name_with_ordinal(self):
        assert parse("March 3rd, 2026") == date(2026, 3, 3)

    def test_slash_format(self):
        assert parse("3/3/2026") == date(2026, 3, 3)


class TestRelativeDates:
    def test_today(self):
        assert parse("today", today=REFERENCE) == REFERENCE

    def test_tomorrow(self):
        assert parse("tomorrow", today=REFERENCE) == date(2026, 5, 14)

    def test_yesterday(self):
        assert parse("yesterday", today=REFERENCE) == date(2026, 5, 12)

    def test_in_n_days(self):
        assert parse("in 3 days", today=REFERENCE) == date(2026, 5, 16)

    def test_n_weeks_from_now(self):
        assert parse("3 weeks from now", today=REFERENCE) == date(2026, 6, 3)

    def test_next_week(self):
        assert parse("next week", today=REFERENCE) == date(2026, 5, 20)


class TestWeekdays:
    # REFERENCE is Wednesday 2026-05-13.
    def test_next_tuesday(self):
        assert parse("next Tuesday", today=REFERENCE) == date(2026, 5, 19)

    def test_last_friday(self):
        assert parse("last Friday", today=REFERENCE) == date(2026, 5, 8)

    def test_this_friday(self):
        assert parse("this Friday", today=REFERENCE) == date(2026, 5, 15)


class TestDefaultToday:
    def test_today_defaults_to_current_date(self):
        assert parse("today") == date.today()

    def test_tomorrow_defaults_to_current_date(self):
        from datetime import timedelta

        assert parse("tomorrow") == date.today() + timedelta(days=1)


class TestReturnType:
    def test_returns_date_instance(self):
        result = parse("2026-03-03")
        assert isinstance(result, date)

    @pytest.mark.parametrize(
        "expression",
        ["today", "tomorrow", "next Tuesday", "March 3, 2026"],
    )
    def test_various_inputs_return_date(self, expression):
        assert isinstance(parse(expression, today=REFERENCE), date)
