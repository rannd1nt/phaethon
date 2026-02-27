"""
Phaethon Example 14: Cloud Compute Costs (Metaclass Grand Finale)
--------------------------------------------------------------
Phaethon isn't just for physics; it handles ANY dimensional logic.
Here we synthesize a complex Cloud Billing rate: Currency / (Data * Time)
to calculate exact server compute costs dynamically.
"""

import phaethon as ptn
from phaethon import BaseUnit, axiom, u
from decimal import Decimal

# 1. Bootstrapping a non-physics dimension: Currency
class CurrencyUnit(BaseUnit):
    dimension = "currency"

class USDollar(CurrencyUnit):
    symbol = "USD"
    base_multiplier = 1.0

# 2. Grand Finale Algebra: Cost = USD / (Gigabytes * Hours)
@axiom.derive(USDollar / (u.Gigabyte * u.Hour))
class CloudComputeRate(BaseUnit):
    symbol = "$/GB-hr"

print("--- AWS/GCP COMPUTE BILLING ENGINE ---")

# Scenario: A Data Processing Job uses 64 GB of RAM for 4.5 Hours.
# The Cloud Provider charges $0.05 per GB-hour.
job_ram = u.Gigabyte(64.0)
job_duration = u.Hour(4.5)
aws_rate = CloudComputeRate(Decimal('0.05'))

print(f"RAM Allocated  : {job_ram}")
print(f"Job Duration   : {job_duration}")
print(f"Provider Rate  : {aws_rate.mag} {aws_rate.symbol}")

# Dimensional Math: Data * Time = Compute Load
compute_load = job_ram * job_duration

# Compute Load * Rate = Total Cost (Data * Time * (Currency / (Data * Time)) -> Currency!)
total_cost = compute_load * aws_rate

print(f"\nRaw Synthesized Cost : {total_cost} (Dimension: {ptn.dimof(total_cost)})")

# Ensure it safely lands as pure US Dollars
final_bill = USDollar(total_cost.mag)

print("="*40)
print(f"FINAL INVOICE : ${final_bill.mag:,.2f} USD")
print("="*40)