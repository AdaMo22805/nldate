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

    def test_slash_format_two_digit_year(self):
        assert parse("12/04/25") == date(2025, 12, 4)

    def test_slash_format_two_digit_year_no_leading_zero(self):
        assert parse("12/4/25") == date(2025, 12, 4)

    def test_slash_format_year_first(self):
        assert parse("2025/12/04") == date(2025, 12, 4)


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

    def test_in_n_months(self):
        assert parse("in 3 months", today=REFERENCE) == date(2026, 8, 13)

    def test_n_months_from_now(self):
        assert parse("3 months from now", today=REFERENCE) == date(2026, 8, 13)

    def test_in_n_months_clamps_short_month(self):
        # Jan 31 + 1 month should clamp to the last day of Feb.
        assert parse("in 1 month", today=date(2026, 1, 31)) == date(2026, 2, 28)

    def test_in_n_months_crosses_year(self):
        assert parse("in 12 months", today=REFERENCE) == date(2027, 5, 13)

    def test_in_n_years(self):
        assert parse("in 2 years", today=REFERENCE) == date(2028, 5, 13)

    def test_n_years_from_now(self):
        assert parse("2 years from now", today=REFERENCE) == date(2028, 5, 13)

    def test_in_n_years_clamps_leap_day(self):
        # Feb 29 + 1 year should clamp to Feb 28 in a non-leap year.
        assert parse("in 1 year", today=date(2024, 2, 29)) == date(2025, 2, 28)

    def test_n_days_ago(self):
        assert parse("3 days ago", today=REFERENCE) == date(2026, 5, 10)

    def test_n_months_ago(self):
        assert parse("3 months ago", today=REFERENCE) == date(2026, 2, 13)

    def test_n_years_ago(self):
        assert parse("1 year ago", today=REFERENCE) == date(2025, 5, 13)

    def test_a_week_ago(self):
        assert parse("a week ago", today=REFERENCE) == date(2026, 5, 6)

    def test_two_weeks_ago(self):
        assert parse("two weeks ago", today=REFERENCE) == date(2026, 4, 29)

    def test_three_days_ago(self):
        assert parse("three days ago", today=REFERENCE) == date(2026, 5, 10)

    def test_one_day_ago(self):
        assert parse("one day ago", today=REFERENCE) == date(2026, 5, 12)

    def test_in_five_days(self):
        assert parse("in five days", today=REFERENCE) == date(2026, 5, 18)

    def test_ten_months_from_now(self):
        assert parse("ten months from now", today=REFERENCE) == date(2027, 3, 13)


class TestWeekdays:
    # REFERENCE is Wednesday 2026-05-13.
    def test_next_tuesday(self):
        assert parse("next Tuesday", today=REFERENCE) == date(2026, 5, 19)

    def test_last_friday(self):
        assert parse("last Friday", today=REFERENCE) == date(2026, 5, 8)

    def test_last_monday(self):
        # The most recent past Monday (REFERENCE is Wed, so 2 days earlier).
        assert parse("last Monday", today=REFERENCE) == date(2026, 5, 11)

    def test_this_friday(self):
        assert parse("this Friday", today=REFERENCE) == date(2026, 5, 15)

    def test_next_friday(self):
        # The upcoming Friday (REFERENCE is Wed, so 2 days later).
        assert parse("next Friday", today=REFERENCE) == date(2026, 5, 15)

    def test_two_fridays_from_now(self):
        assert parse("2 fridays from now", today=REFERENCE) == date(2026, 5, 22)

    def test_two_fridays_ago(self):
        assert parse("2 fridays ago", today=REFERENCE) == date(2026, 5, 1)

    def test_one_friday_from_now(self):
        # The next upcoming Friday — this Friday, not next week's.
        assert parse("1 friday from now", today=REFERENCE) == date(2026, 5, 15)

    def test_three_mondays_from_now(self):
        assert parse("3 mondays from now", today=REFERENCE) == date(2026, 6, 1)

    def test_two_sundays_ago(self):
        assert parse("2 sundays ago", today=REFERENCE) == date(2026, 5, 3)

    def test_two_fridays_word_count(self):
        assert parse("two fridays from now", today=REFERENCE) == date(2026, 5, 22)


class TestDefaultToday:
    def test_today_defaults_to_current_date(self):
        assert parse("today") == date.today()

    def test_tomorrow_defaults_to_current_date(self):
        from datetime import timedelta

        assert parse("tomorrow") == date.today() + timedelta(days=1)


class TestCaseInsensitive:
    def test_uppercase_keyword(self):
        assert parse("TODAY", today=REFERENCE) == REFERENCE

    def test_mixed_case_keyword(self):
        assert parse("ToMoRrOw", today=REFERENCE) == date(2026, 5, 14)

    def test_lowercase_month_name(self):
        assert parse("march 3, 2026") == date(2026, 3, 3)

    def test_uppercase_month_name(self):
        assert parse("MARCH 3, 2026") == date(2026, 3, 3)

    def test_uppercase_weekday(self):
        assert parse("next TUESDAY", today=REFERENCE) == date(2026, 5, 19)

    def test_title_case_modifier_and_weekday(self):
        assert parse("Next Tuesday", today=REFERENCE) == date(2026, 5, 19)

    def test_uppercase_relative_phrase(self):
        assert parse("IN 3 DAYS", today=REFERENCE) == date(2026, 5, 16)


class TestWhitespace:
    def test_leading_and_trailing_whitespace(self):
        assert parse("  today  ", today=REFERENCE) == REFERENCE

    def test_multiple_internal_spaces(self):
        assert parse("March  3,  2026") == date(2026, 3, 3)


class TestSingularUnits:
    def test_in_one_day(self):
        assert parse("in 1 day", today=REFERENCE) == date(2026, 5, 14)

    def test_in_one_week(self):
        assert parse("in 1 week", today=REFERENCE) == date(2026, 5, 20)

    def test_in_one_month(self):
        assert parse("in 1 month", today=REFERENCE) == date(2026, 6, 13)

    def test_in_one_year(self):
        assert parse("in 1 year", today=REFERENCE) == date(2027, 5, 13)


class TestAbbreviations:
    def test_month_abbreviation(self):
        assert parse("Mar 3, 2026") == date(2026, 3, 3)

    def test_month_abbreviation_with_period(self):
        assert parse("Dec. 1, 2025") == date(2025, 12, 1)

    def test_weekday_abbreviation_with_modifier(self):
        assert parse("next Tue", today=REFERENCE) == date(2026, 5, 19)

    def test_weekday_abbreviation_last(self):
        assert parse("last Fri", today=REFERENCE) == date(2026, 5, 8)


class TestMonthWithoutYear:
    def test_defaults_to_today_year(self):
        assert parse("March 3", today=REFERENCE) == date(2026, 3, 3)

    def test_with_ordinal_no_year(self):
        assert parse("March 3rd", today=REFERENCE) == date(2026, 3, 3)


class TestYearBoundaries:
    def test_tomorrow_crosses_year(self):
        assert parse("tomorrow", today=date(2026, 12, 31)) == date(2027, 1, 1)

    def test_yesterday_crosses_year(self):
        assert parse("yesterday", today=date(2026, 1, 1)) == date(2025, 12, 31)

    def test_next_week_crosses_year(self):
        assert parse("next week", today=date(2026, 12, 28)) == date(2027, 1, 4)


class TestSameWeekday:
    # REFERENCE is Wednesday 2026-05-13.
    def test_this_weekday_returns_today(self):
        assert parse("this Wednesday", today=REFERENCE) == REFERENCE

    def test_next_weekday_returns_one_week_later(self):
        assert parse("next Wednesday", today=REFERENCE) == date(2026, 5, 20)


class TestAnchoredOffsets:
    def test_n_days_before_month_name_date(self):
        assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)

    def test_n_days_after_month_name_date(self):
        assert parse("5 days after December 1st, 2025") == date(2025, 12, 6)

    def test_n_days_since_month_name_date(self):
        # "since" resolves in the same direction as "after".
        assert parse("5 days since December 1st, 2025") == date(2025, 12, 6)

    def test_word_count_before_date(self):
        assert parse("two days before March 3, 2026") == date(2026, 3, 1)

    def test_article_before_date(self):
        assert parse("a week before December 1st, 2025") == date(2025, 11, 24)

    def test_weeks_before_iso_date(self):
        assert parse("2 weeks before 2025-12-01") == date(2025, 11, 17)

    def test_months_after_slash_date(self):
        assert parse("3 months after 1/1/2026") == date(2026, 4, 1)

    def test_days_before_relative_anchor(self):
        assert parse("5 days before today", today=REFERENCE) == date(2026, 5, 8)

    def test_compound_offset_with_and(self):
        # 2025-12-01 minus 2 years minus 3 months -> 2023-09-01.
        assert parse("2 years and 3 months before Dec. 1, 2025") == date(2023, 9, 1)

    def test_compound_offset_with_ampersand(self):
        assert parse("2 years & 3 months before Dec. 1, 2025") == date(2023, 9, 1)

    def test_compound_offset_with_comma(self):
        assert parse("2 years, 3 months before Dec. 1, 2025") == date(2023, 9, 1)

    def test_compound_offset_after(self):
        # 2026-01-01 plus 1 year plus 6 months -> 2027-07-01.
        assert parse("1 year and 6 months after January 1, 2026") == date(2027, 7, 1)

    def test_compound_offset_days_and_weeks(self):
        # 2025-12-01 minus 5 days minus 2 weeks -> 2025-11-12.
        assert parse("5 days and 2 weeks before December 1, 2025") == date(2025, 11, 12)

    def test_compound_offset_with_relative_anchor(self):
        # REFERENCE (2026-05-13) plus 3 weeks plus 4 days -> 2026-06-07.
        assert parse("3 weeks and 4 days since today", today=REFERENCE) == date(
            2026, 6, 7
        )

    def test_compound_offset_with_word_count(self):
        # 2026-03-03 minus 2 months minus 3 days -> 2025-12-31.
        assert parse("two months and three days before March 3, 2026") == date(
            2025, 12, 31
        )


class TestInvalidInputs:
    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse("")

    def test_gibberish_raises(self):
        with pytest.raises(ValueError):
            parse("asdfjkl")

    def test_invalid_month_raises(self):
        with pytest.raises(ValueError):
            parse("2026-13-01")

    def test_invalid_day_raises(self):
        with pytest.raises(ValueError):
            parse("2026-02-30")

    def test_unsupported_phrase_raises(self):
        with pytest.raises(ValueError):
            parse("day after tomorrow")


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
