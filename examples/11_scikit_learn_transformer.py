"""
Chisa Example 11: Scikit-Learn Custom Transformer
-------------------------------------------------
Build a custom ML `BaseEstimator` that autonomously normalizes 
heterogeneous unit arrays before training a Random Forest.
"""

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import chisa as cs
from chisa import u

# 1. Define the physical contract using Chisa Schema
class FeatureSchema(cs.Schema):
    weight_kg: u.Kilogram = cs.Field(source="weight_raw", parse_string=True, on_error='coerce')
    top_speed_ms: u.MeterPerSecond = cs.Field(source="speed_raw", parse_string=True, on_error='coerce')

# 2. Wrap the Schema in a Scikit-Learn standard Transformer
class ChisaNormalizer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        # Normalize units and fill bad data with median/0 (ML models hate NaNs)
        clean_df = FeatureSchema.normalize(X, keep_unmapped=True, drop_raw=True)
        return clean_df.fillna(0)

# 3. Execution
X_train = pd.DataFrame({
    'Car_Model': ['Sedan-A', 'Truck-B', 'Sports-C'],
    'weight_raw': ["3000 lbs", "5000 kg", "1.5 t"],
    'speed_raw': ["120 mph", "100 km/h", "80 m/s"]
})

print("--- RAW MACHINE LEARNING FEATURES ---")
print(X_train)

# In a real app, you would pass this to sklearn's make_pipeline()
transformer = ChisaNormalizer()
X_clean = transformer.transform(X_train)

print("\n--- ML-READY FEATURES (NORMALIZED) ---")
print(X_clean)