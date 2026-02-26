"""
Chisa Example 09: End-to-End ESG Pipeline
-----------------------------------------
The Grand Unified Theory of Chisa. This script demonstrates how to:
1. Synthesize a custom dimension (Carbon Intensity) from scratch.
2. Clean messy Pandas data into that custom dimension using Schema.
3. Protect business logic using @require and @prepare.
"""

import pandas as pd
import chisa as cs
from chisa import axiom, u
from chisa.core.base import BaseUnit

# =========================================================================
# STAGE 1: SYNTHESIS (Defining New Physical Laws)
# =========================================================================
@axiom.bound(min_val=0, msg="CRITICAL: Carbon emissions cannot be negative!")
class CarbonIntensity(BaseUnit):
    dimension = "carbon_intensity"

@axiom.derive(u.Kilogram / u.KilowattHour)
class KgCO2PerKWh(CarbonIntensity):
    symbol = "kgCO2/kWh"
    # Best Practice: Aliases allow Schema Regex to intelligently capture dirty text
    aliases = ["kg/kWh", "kilogram per kwh", "kgCO2 per kWh"] 


# =========================================================================
# STAGE 2: ALGORITHM GUARDRAILS (Business Logic Protection)
# =========================================================================
# Lock the function: ONLY accepts our custom 'carbon_intensity' dimension
@axiom.require(intensity=CarbonIntensity)
# Force the input to be automatically extracted as a standard float (KgCO2PerKWh)
@axiom.prepare(intensity=KgCO2PerKWh)
def calculate_carbon_tax(intensity: float, energy_produced_mwh: float):
    """
    Calculates carbon tax. Rate: $0.05 per Kg CO2.
    Thanks to @prepare, the 'intensity' variable here is safely passed 
    as a pure float (.mag) in the standard KgCO2PerKWh unit. Highly secure!
    """
    total_kwh = energy_produced_mwh * 1000
    total_kg_co2 = intensity * total_kwh
    return total_kg_co2 * 0.05


# =========================================================================
# STAGE 3: DATA PIPELINE (Schema Integration)
# =========================================================================
class FactoryESGSchema(cs.Schema):
    # Use our custom class directly in Type Hinting!
    emission_rate: KgCO2PerKWh = cs.Field(
        source="Raw_Sensor", 
        parse_string=True, 
        on_error='coerce', 
        round=2
    )

print("--- 1. RAW FACTORY TELEMETRY ---")
df_raw = pd.DataFrame({
    'Factory_ID': ['F-London', 'F-NewYork', 'F-Tokyo'],
    'Energy_MWh': [15.0, 20.0, 5.0],
    # Dirty text data using various newly registered aliases
    'Raw_Sensor': ["1000 kg/kWh", "1250.5 kgCO2 per kWh", "-50 kgCO2/kWh"] 
})
print(df_raw)

print("\n--- 2. CHISA NORMALIZED ESG DATA ---")
# The Schema reads the Registry, finds our custom unit, and parses the text
clean_df = FactoryESGSchema.normalize(df_raw, keep_unmapped=True, drop_raw=True)
print(clean_df)

print("\n--- 3. EXECUTING GUARDED ALGORITHM ---")
# Apply the carbon tax function to the cleaned data
taxes = []
for idx, row in clean_df.iterrows():
    if pd.isna(row['emission_rate']):
        taxes.append("INVALID SENSOR (NaN)")
        continue
        
    # Re-instantiate our custom Unit from the dataframe
    # This simulates input from a user/API passed to a mathematical function
    safe_intensity_unit = KgCO2PerKWh(row['emission_rate'])
    
    # This function is strictly protected by @require and @prepare
    tax = calculate_carbon_tax(intensity=safe_intensity_unit, energy_produced_mwh=row['Energy_MWh'])
    taxes.append(f"${tax:,.2f}")

clean_df['Carbon_Tax_USD'] = taxes
print(clean_df[['Factory_ID', 'emission_rate', 'Carbon_Tax_USD']])