"""
Chisa Example 13: Dynamic Alert Thresholds (IoT Streaming)
----------------------------------------------------------
In real industrial IoT, safety limits aren't always static.
This script uses a Chisa Schema to normalize temperatures, then applies 
dynamic safety thresholds based on the machine's active cooling mode.
"""

import pandas as pd
import chisa as cs
from chisa import u

class NuclearReactorSchema(cs.Schema):
    # Standardize all incoming thermal telemetry to strict Celsius
    core_temp: u.Celsius = cs.Field(source="Temp_Raw", parse_string=True, on_error='coerce', round=1)

    @cs.post_normalize
    def dynamic_safety_check(cls, df):
        print("[Security Hook] Evaluating dynamic thermal bounds...")
        # Rule 1: If Cooling is OFF, max temp is 100 C
        # Rule 2: If Cooling is ON, max temp is 500 C
        danger_mask = ((df['Cooling'] == 'OFF') & (df['core_temp'] > 100)) | \
                      ((df['Cooling'] == 'ON') & (df['core_temp'] > 500))

        if danger_mask.any():
            breach_count = danger_mask.sum()
            print(f"SCRAM INITIATED! {breach_count} reactor(s) breached dynamic thermal limits!")
            # In production, trigger an API webhook or PagerDuty alert here
            df.loc[danger_mask, 'STATUS'] = 'CRITICAL'
        
        df['STATUS'] = df['STATUS'].fillna('SAFE')
        return df

print("--- REACTOR TELEMETRY STREAM ---")

df_stream = pd.DataFrame({
    'Reactor_ID': ['R-Alpha', 'R-Beta', 'R-Gamma', 'R-Delta'],
    'Cooling': ['ON', 'ON', 'OFF', 'OFF'],
    'Temp_Raw': ["450 C", "800 F", "85 C", "250 F"] # 250 F is ~121 C (Danger if Cooling OFF!)
})

print("1. Raw Incoming Data:")
print(df_stream)

print("\n2. Processing Pipeline:")
# Keep the metadata columns intact!
safe_df = NuclearReactorSchema.normalize(df_stream, keep_unmapped=True, drop_raw=True)

print("\n3. Normalized System State:")
print(safe_df)