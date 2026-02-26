"""
Chisa Example 04: Energy Grid Audits (Lifecycle Hooks)
------------------------------------------------------
Inject your own business logic into the validation pipeline. 
This script filters out inactive meters before standardizing raw energy data.
"""

import pandas as pd
import chisa as cs
from chisa import u

class EnergyAuditSchema(cs.Schema):
    total_energy: u.KilowattHour = cs.Field(
        source="Raw_Usage", parse_string=True, on_error='coerce', round=2
    )

    @cs.pre_normalize
    def filter_active_meters(cls, raw_df):
        print("[Hook] Filtering out INACTIVE meters...")
        return raw_df[raw_df['Status'] == 'ACTIVE'].copy()

df_grid = pd.DataFrame({
    'Meter_ID': ['M-101', 'M-102', 'M-103', 'M-104'],
    'Status': ['ACTIVE', 'INACTIVE', 'ACTIVE', 'ACTIVE'],
    'Raw_Usage': ["5 MMBtu", "9000 kWh", "15000 kWh", "50000000 J"]
})

print("--- RAW GRID EXPORT ---")
print(df_grid)

clean_df = EnergyAuditSchema.normalize(df_grid)

print("\n--- NORMALIZED KWH AUDIT ---")
print(clean_df)