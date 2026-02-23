"""
Chisa Example 15: Scikit-Learn Custom Pipeline Transformer
----------------------------------------------------------
In Machine Learning, mixing datasets with different units (e.g., Celsius and Fahrenheit) 
will destroy your model's accuracy.

This script demonstrates how to wrap Chisa into a Scikit-Learn `TransformerMixin`.
This allows Chisa to autonomously normalize units inside an automated ML Pipeline!
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from chisa import convert

class ChisaNormalizer(BaseEstimator, TransformerMixin):
    """A Scikit-Learn custom transformer powered by Chisa."""
    
    def __init__(self, target_unit: str, source_unit: str):
        self.target_unit = target_unit
        self.source_unit = source_unit

    def fit(self, X, y=None):
        return self  # Nothing to fit for unit conversion

    def transform(self, X, y=None):
        # We assume X is a 2D NumPy array or Pandas column.
        # Chisa's convert() processes the entire array natively!
        normalized_array = convert(X, self.source_unit).to(self.target_unit).use(format='raw').resolve()
        return normalized_array.reshape(-1, 1)


print("=== Building a Unit-Safe ML Pipeline ===")

# Mock dataset: Temperatures from different sensors (all in Fahrenheit)
dirty_data = pd.DataFrame({
    'sensor_temp_f': [70.0, 85.0, 100.5, 45.0, 32.0, 212.0]
})
print("Input Data (Fahrenheit):")
print(dirty_data['sensor_temp_f'].values)

# Create an ML Pipeline: 
# 1. Normalize F to Celsius using Chisa.
# 2. Scale the data statistically using Scikit-Learn's StandardScaler.
ml_pipeline = Pipeline([
    ('chisa_unit_fixer', ChisaNormalizer(source_unit='F', target_unit='C')),
    ('statistical_scaler', StandardScaler())
])

# Execute the pipeline!
ready_for_ai = ml_pipeline.fit_transform(dirty_data['sensor_temp_f'].values)

print("\nOutput Data (Celsius, Statistically Scaled for AI):")
print(np.round(ready_for_ai.flatten(), 3))