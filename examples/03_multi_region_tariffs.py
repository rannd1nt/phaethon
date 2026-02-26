"""
Chisa Example 03: Multi-Region Tariffs (Dynamic Columns)
--------------------------------------------------------
When databases store values and units in separate columns, Chisa uses 
`unit_col` to dynamically resolve them row-by-row while enforcing bounds.
"""

import pandas as pd
import chisa as cs
from chisa import u

class TariffSchema(cs.Schema):
    billable_weight: u.Kilogram = cs.Field(
        source="weight_val", unit_col="unit_code", on_error='coerce', round=3, min=0
    )

    @cs.post_normalize
    def calculate_global_tariff(cls, df):
        # Apply a flat $5.50 per kg shipping tariff
        df['shipping_cost_usd'] = df['billable_weight'] * 5.50
        return df

df_shipping = pd.DataFrame({
    'Tracking_ID': ['TRK-01', 'TRK-02', 'TRK-03', 'TRK-04'],
    'weight_val': [50.0, 15.5, 200.0, -5.0], # -5.0 is an anomaly
    'unit_code': ['lbs', 'kg', 'oz', 'kg'] 
})

print("--- RAW SHIPPING MANIFEST ---")
print(df_shipping)

clean_df = TariffSchema.normalize(df_shipping)
final_report = pd.concat([df_shipping[['Tracking_ID']], clean_df], axis=1)

print("\n--- GLOBAL TARIFF REPORT ---")
print(final_report)