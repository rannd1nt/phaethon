"""
Phaethon Example 07: Financial Billing Precision (.mag vs .exact)
--------------------------------------------------------------
When converting units for financial billing, standard Python floats 
suffer from rounding errors (e.g., 0.1 + 0.2 = 0.300000000004). 
Phaethon safely handles `decimal.Decimal` to preserve absolute financial integrity.
"""

from decimal import Decimal
from phaethon import u

print("--- CLOUD STORAGE BILLING ENGINE ---")
# A customer transfers exactly 0.1 Petabytes, 3 times.
# Price is $50,000 per Terabyte.

# 1. The Machine Learning / Math approach (Using .mag / Floats)
pb_transfer_float = u.Petabyte(0.1)
tb_converted_float = pb_transfer_float.to(u.Terabyte).mag

# Floating point error accumulation: 0.1 * 3 in floats is NOT exactly 0.3
total_tb_float = tb_converted_float * 3
revenue_float = total_tb_float * 50_000

print(f"Float Calculation (.mag)  : {total_tb_float} TB")
print(f"Float Revenue Billed      : ${revenue_float:,.2f} (INACCURATE!)\n")


# 2. The Financial Audit approach (Using .exact / Decimals)
pb_transfer_exact = u.Petabyte(Decimal('0.1'))
tb_converted_exact = pb_transfer_exact.to(u.Terabyte).exact

# Decimals preserve absolute mathematical truth
total_tb_exact = tb_converted_exact * 3
revenue_exact = total_tb_exact * Decimal('50000')

print(f"Decimal Calculation (.exact): {total_tb_exact} TB")
print(f"Decimal Revenue Billed      : ${revenue_exact:,.2f} (PERFECT MATCH)")

loss = Decimal(str(revenue_float)) - revenue_exact
print(f"\nUsing floats would have caused an accounting anomaly of ${loss:,.2f}!")