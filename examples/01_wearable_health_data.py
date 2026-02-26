"""
Chisa Example 01: Wearable Health Data Schema
---------------------------------------------
This script demonstrates parsing messy strings from various smartwatches.
It standardizes heart rates, body temperatures, and safely handles 
anomalies (like temperatures violating Absolute Zero).
"""

import pandas as pd
import chisa as cs
from chisa import u

class HealthDataSchema(cs.Schema):
    heart_rate: u.BeatsPerMinute = cs.Field(
        source="HR_Raw", parse_string=True, on_error='coerce', min=0
    )
    energy_burned: u.Kilocalorie = cs.Field(
        source="Calories", parse_string=True, on_error='coerce', round=2
    )
    body_temp: u.Celsius = cs.Field(
        source="Temp", parse_string=True, on_error='coerce', round=1
    )

df_smartwatch = pd.DataFrame({
    'Device': ['Garmin', 'Apple Watch', 'Fitbit', 'Broken Sensor'],
    'HR_Raw': ["120 bpm", "95 beats per minute", "88", "NaN"],
    'Calories': ["450 kcal", "300 Cal", "250000 cal", "0"],
    'Temp': ["36.5 C", "98.6 F", "37.0 °C", "-500 C"] # Violates Absolute Zero
})

print("--- RAW SMARTWATCH EXPORT ---")
print(df_smartwatch)

clean_df = HealthDataSchema.normalize(df_smartwatch, keep_unmapped=True)

print("\n--- CHISA NORMALIZED HEALTH DATA ---")
print(clean_df)