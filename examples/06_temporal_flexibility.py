"""
Chisa Example 06: Temporal Flexibility (.flex)
----------------------------------------------
Time is unique because humans rarely read massive durations in pure scalars.
We don't say "I am 946,080,000 seconds old", we say "I am 30 years old".

This script showcases the `.flex()` method, an exclusive feature of the 
Time dimension that breaks down raw seconds into natural language.
"""

from chisa.units.time import Second

print("=== 1. The .flex() Breakdown ===")
# Let's say a server has been running for this many seconds
uptime_seconds = Second(123456789.0)

print(f"Raw Input: {uptime_seconds.format(delim=True)}")

# Automatically breaks it down into the largest logical whole units
human_readable = uptime_seconds.flex()
print(f"Uptime   : {human_readable}")
# Output: "3 years 10 months 4 weeks 18 hours 33 minutes 9 seconds"


print("\n=== 2. Customizing the Flex Range ===")
# Sometimes you don't want years or months, maybe just Days and Hours
# for a shorter project timeline.

project_duration = Second(500000.0)
print(f"Project  : {project_duration.format(delim=True)}")

# Limiting the breakdown range between 'day' and 'minute'
custom_flex = project_duration.flex(range=("day", "minute"))
print(f"Timeline : {custom_flex}")
# Output: "5 days 18 hours 53 minutes"