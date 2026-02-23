"""
Time and Duration Dimension Module.

This module quantifies the progression of events. It covers standard SI durations, 
calendar metrics, and massive human epochs (e.g., Centuries, Millenniums).
It also includes unique formatting utilities to break raw scalar seconds down 
into human-readable natural language strings.
The absolute base unit for this dimension is the Second (s).
"""

from decimal import Decimal
from typing import Tuple, Optional, Union
from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const

@axiom.bound(min_val=0, msg="Elapsed time duration cannot be negative.")
class TimeUnit(BaseUnit):
    """
    The primary parent class for the Time dimension.
    Features a specialized `.flex()` method to parse scalar seconds into 
    human-readable multi-unit strings (e.g., '1 year 2 months 5 days').
    """
    dimension = "time"

    # Static hierarchy defining unit magnitudes in seconds for the flex formatter
    _FLEX_HIERARCHY = [
        ("millennium", Decimal(str(const.JULIAN_YEAR_TO_SECOND * 1000))),
        ("century", Decimal(str(const.JULIAN_YEAR_TO_SECOND * 100))),
        ("decade", Decimal(str(const.JULIAN_YEAR_TO_SECOND * 10))),
        ("year", Decimal(str(const.JULIAN_YEAR_TO_SECOND))),
        ("month", Decimal(str(const.JULIAN_MONTH_TO_SECOND))),
        ("week", Decimal(str(const.WEEK_TO_SECOND))),
        ("day", Decimal(str(const.DAY_TO_SECOND))),
        ("hour", Decimal(str(const.HOUR_TO_SECOND))),
        ("minute", Decimal(str(const.MINUTE_TO_SECOND))),
        ("second", Decimal("1"))
    ]

    def flex(self, range: Tuple[Optional[str], Optional[str]] = (None, None), delim: Union[bool, str] = True) -> str:
        """
        Deconstructs the total time duration into a natural language format.
        
        Args:
            range: The upper and lower bounds for the output units.
            delim: Whether to include thousands separators in the numbers.

        Returns:
            str: The human-readable formatted time string.
        """
        import numpy as np

        lower_bound, upper_bound = range
        valid_units = [u[0] for u in self._FLEX_HIERARCHY]

        start_index = valid_units.index(lower_bound) if lower_bound else 0
        end_index = valid_units.index(upper_bound) if upper_bound else len(valid_units) - 1

        if start_index > end_index:
            raise ValueError("Invalid range: lower bound must be a larger unit than upper bound")

        allowed_hierarchy = self._FLEX_HIERARCHY[start_index:end_index + 1]
        
        raw_remaining = self._to_base_value()

        if isinstance(raw_remaining, np.ndarray):
            raise TypeError("The .flex() method is intended for scalars and does not support NumPy arrays.")

        remaining = Decimal(str(raw_remaining))
        result = []

        for unit_name, unit_seconds in allowed_hierarchy:
            count = remaining // unit_seconds
            if count > 0:
                count_str = f"{int(count):,}" if delim else str(int(count))
                result.append(f"{count_str} {unit_name}{'s' if int(count) > 1 else ''}")
                remaining -= count * unit_seconds

            if remaining < Decimal("0.0001"):
                break

        if not result:
            return "0 seconds"

        return " ".join(result)


# =========================================================================
# 1. BASE UNIT & SMALLER
# =========================================================================
class Second(TimeUnit):
    symbol = "s"
    aliases = ["sec", "second", "seconds"]
    base_multiplier = 1.0

class Millisecond(TimeUnit):
    symbol = "ms"
    aliases = ["millisecond", "milliseconds", "millis"]
    base_multiplier = 1e-3

class Microsecond(TimeUnit):
    symbol = "μs"
    aliases = ["us", "microsecond", "microseconds", "micros"]
    base_multiplier = 1e-6

class Nanosecond(TimeUnit):
    symbol = "ns"
    aliases = ["nanosecond", "nanoseconds", "nanos"]
    base_multiplier = 1e-9


# =========================================================================
# 2. COMMON HUMAN TIME
# =========================================================================
class Minute(TimeUnit):
    symbol = "min"
    aliases = ["minute", "minutes"]
    base_multiplier = const.MINUTE_TO_SECOND

class Hour(TimeUnit):
    symbol = "h"
    aliases = ["hr", "hour", "hours"]
    base_multiplier = const.HOUR_TO_SECOND

class Day(TimeUnit):
    symbol = "d"
    aliases = ["day", "days"]
    base_multiplier = const.DAY_TO_SECOND

class Week(TimeUnit):
    symbol = "w"
    aliases = ["wk", "week", "weeks"]
    base_multiplier = const.WEEK_TO_SECOND

class Month(TimeUnit):
    symbol = "mo"
    aliases = ["m", "month", "months"]
    base_multiplier = const.JULIAN_MONTH_TO_SECOND

class Year(TimeUnit):
    symbol = "y"
    aliases = ["yr", "year", "years"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND


# =========================================================================
# 3. CALENDAR & ACADEMIC TERMS
# =========================================================================
class Bimonth(TimeUnit):
    symbol = "bimonth"
    aliases = ["bimonthly"]
    base_multiplier = const.JULIAN_MONTH_TO_SECOND * 2.0

class Quarter(TimeUnit):
    symbol = "quarter"
    aliases = ["quarters", "triwulan", "trimester", "trimesters"]
    base_multiplier = const.JULIAN_MONTH_TO_SECOND * 3.0

class Quadmester(TimeUnit):
    symbol = "quadmester"
    aliases = ["quadmesters"]
    base_multiplier = const.JULIAN_MONTH_TO_SECOND * 4.0

class Semester(TimeUnit):
    symbol = "semester"
    aliases = ["semesters"]
    base_multiplier = const.JULIAN_MONTH_TO_SECOND * 6.0


# =========================================================================
# 4. ERAS / LONGER PERIODS
# =========================================================================
class Lustrum(TimeUnit):
    symbol = "lustrum"
    aliases = ["lustra"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND * 5.0

class Windu(TimeUnit):
    symbol = "windu"
    aliases = ["windus"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND * 8.0

class Decade(TimeUnit):
    symbol = "decade"
    aliases = ["decades", "dasawarsa"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND * 10.0

class Score(TimeUnit):
    symbol = "score"
    aliases = ["scores"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND * 20.0

class Generation(TimeUnit):
    symbol = "generation"
    aliases = ["generations"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND * 30.0

class Century(TimeUnit):
    symbol = "century"
    aliases = ["centuries"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND * 100.0

class Millennium(TimeUnit):
    symbol = "millennium"
    aliases = ["millennia", "milenium", "millenium"]
    base_multiplier = const.JULIAN_YEAR_TO_SECOND * 1000.0