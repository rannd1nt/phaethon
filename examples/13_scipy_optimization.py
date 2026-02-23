"""
Chisa Example 13: SciPy Optimization Integration
------------------------------------------------
SciPy is the gold standard for scientific optimization, but it only accepts 
pure floats. This script shows how Chisa can validate physical bounds and 
safely inject them into a SciPy optimizer.
"""

from scipy.optimize import minimize
from chisa.units.speed import KilometerPerHour, MeterPerSecond

# We want to find the optimal speed (in m/s) to minimize fuel consumption.
# Let's say drag increases with the square of speed, but going too slow takes too long.
def fuel_consumption_model(speed_ms):
    """A mock formula for fuel consumption based on speed."""
    return 0.05 * speed_ms**2 + (500.0 / speed_ms)

print("=== Optimizing Vehicle Speed with SciPy & Chisa ===")

# 1. We define our safety bounds using Chisa's strict OOP to avoid manual math errors!
min_speed = KilometerPerHour(20.0)
max_speed = KilometerPerHour(120.0)

# 2. We extract the safe .mag (in m/s) to feed into SciPy
bounds = [(
    min_speed.to(MeterPerSecond).mag, 
    max_speed.to(MeterPerSecond).mag
)]

# Initial guess (e.g., 50 km/h -> converted to m/s)
x0 = [KilometerPerHour(50.0).to(MeterPerSecond).mag]

# 3. Run SciPy optimization (Pure float execution = High Performance)
result = minimize(fuel_consumption_model, x0, bounds=bounds)

optimal_speed_ms = result.x[0]

# 4. Wrap the pure float result back into Chisa to present it nicely!
optimal_chisa_speed = MeterPerSecond(optimal_speed_ms)

print(f"Optimal Speed (m/s)  : {optimal_chisa_speed.format(prec=2, tag=True)}")
print(f"Optimal Speed (km/h) : {optimal_chisa_speed.to(KilometerPerHour).format(prec=2, tag=True)}")