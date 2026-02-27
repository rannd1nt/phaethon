"""
Phaethon Example 12: Handling Sensor Drift
---------------------------------------
Use Phaethon's vectorized algebra to neutralize factory machine 
calibration errors (drift) instantly across thousands of records.
"""

import numpy as np
from phaethon import u

print("--- FACTORY SENSOR CALIBRATION ---")

# Scenario: A batch of 5 temperature sensors reading a furnace.
# Calibration tests show they are reading +2.5 °C too hot (Drift).
raw_sensor_readings = np.array([450.0, 452.5, 449.0, 455.0, 451.0])

print(f"Raw Furnace Readings (°C) : {raw_sensor_readings}")

# Vectorize the data
furnace_temps = u.Celsius(raw_sensor_readings)
known_drift = u.Celsius(2.5)

# Subtract the drift across the entire array instantly
# Phaethon allows this dimensional subtraction safely!
calibrated_temps = furnace_temps - known_drift

print(f"Calibrated Readings (°C)  : {calibrated_temps.mag}")

# Ensure the corrected temperatures are safely converted to Fahrenheit for the US client
client_report_f = calibrated_temps.to(u.Fahrenheit).mag
print(f"Client Report (°F)        : {np.round(client_report_f, 1)}")