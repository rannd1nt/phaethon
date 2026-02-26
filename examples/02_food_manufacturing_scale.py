"""
Chisa Example 02: Food Manufacturing Scale
------------------------------------------
This script safely converts kitchen imperial units (cups, fluid ounces, 
pounds) into strict metric factory standards (Milliliters, Grams) instantly.
"""

import pandas as pd
import chisa as cs
from chisa import u

class RecipeScaleSchema(cs.Schema):
    liquid_vol: u.Milliliter = cs.Field(
        source="Liquid_Input", parse_string=True, on_error='coerce', round=1
    )
    dry_mass: u.Gram = cs.Field(
        source="Dry_Weight", parse_string=True, on_error='coerce', round=1
    )

df_recipe = pd.DataFrame({
    'Ingredient': ['Water', 'Milk', 'Flour', 'Sugar'],
    'Liquid_Input': ["2 cups", "15 fl oz", None, "3 tbsp"],
    'Dry_Weight': [None, None, "2.5 lbs", "15 oz"]
})

print("--- RAW KITCHEN RECIPE ---")
print(df_recipe)

factory_df = RecipeScaleSchema.normalize(df_recipe)

print("\n--- STANDARDIZED FACTORY BATCH (METRIC) ---")
print(factory_df)