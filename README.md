> ⚠️ **ARCHIVAL NOTICE**
> 
> This branch contains the legacy source code for **Unitflex**, the early predecessor to the Phaethon. This project is no longer actively maintained and is preserved here purely for historical and archival purposes.
> 
> 👉 **Looking for the active project?** Please visit the [`main branch`](https://github.com/rannd1nt/phaethon/tree/main) to explore **Phaethon**, the completely re-architected, Unit-Aware Data Pipeline Schem and Semantic Data Transformation with NumPy-vectorized dimensional algebra engine.

# What is Unitflex? 📦

**Unitflex** is a Python library for converting values between various measurement units such as **length**, **mass**, **volume**, **data**, **pressure** and more.  
It provides a **clean, extensible**, and **user-friendly** interface to perform conversions easily with customizable output formatting and **high precision modes** for professional use.

Designed to be both **beginner-friendly** and **robust enough for engineers**, Unitflex is suitable for daily tasks, education, and advanced scientific projects.  
It even supports a special `"engineering"` mode for precise calculations using `Decimal`.

` repo: https://github.com/zranndts/unit-flex `

---

# Supported Converters 🧪 
**1. Length 📏**<br>
Unitflex provides accurate and versatile length conversion across a wide range of units, from microscopic scales to astronomical distances. This module supports scientific, engineering, daily, and typographic measurements.  
**Supported Unit Categories:**
- **Metric Units (SI)**<br>Standard international metric system units, including:<br>` picometer (pm) `,` nanometer (nm) `,` micrometer (µm) `,` millimeter (mm) `,` centimeter (cm)`,` decimeter (dm) `,` meter (m) `,` kilometer (km) `,` ångström (Å) `
- **Imperial / US Customary Units**<br>Commonly used in the US and UK:<br>` inch (in) `,` foot (ft) `,` yard (yd) `,` mile (mi) `,` nautical mile (nmi) `,` mil/thou `,` league `,` hand `,` barleycorn `
- **Astronomical Units**<br>For measuring vast distances in space:<br>` lightyear (ly) `,` astronomical unit (au) `,` parsec (pc) `
- **Engineering Units**<br>Traditional units used in civil engineering and land surveying:<br>` chain `,` link `,` rod `,` pole `,` perch `,` furlong `
- **Typographic Units**<br>Used in printing and graphic design:<br>` point (pt) `,` pica `
- **Microscopic Units**<br>Extremely small units used in particle physics and microscopy:<br>` femtometer (fm) `,` fermi `

**2. Mass ⚖️**<br>
Unitflex includes a powerful mass converter that supports a broad spectrum of mass and weight units, from microscopic particles to planetary masses. Designed to accommodate scientific, industrial, and historical uses alike.
**Supported Unit Categories:**
- **Metric Units (SI)**<br>Standard international metric system units, including:<br>` milligram (mg) `,` gram (g) `,` kilogram (kg) `,` metric ton (t) `,` quintal `,` ons `
- **Imperial / US Customary Units**<br>Commonly used in the US and UK:<br>` ounce (oz) `,` pound (lb) `,` stone (st) `,` slug `,` dram `
- **Smaller / Scientific Units**<br>Units used for small-scale mass measurements in jewelry and pharmacology:<br>` carat `,` grain `
- **Ton Variants**<br>Regional and system-specific definitions of the ton:<br>` short ton `,` long ton `
- **Astronomical Units**<br>Massive units used in astrophysics for celestial body comparisons:<br>` solar mass (M☉) `,` earth mass (M⊕) `,` lunar mass (M☾) `,` jupiter mass (M♃) `,` saturn mass (M♄) `,` venus mass `,` mars mass `,` mercury mass `,` neptune mass `,` uranus mass `,` pluto mass `,` ceres mass `
- **Quantum Physics Units**<br>Mass derived from energy equivalents:<br>` electronvolt per c² (eV/c²) `
- **Atomic / Microscopic Units**<br>Extremely small mass units used in particle physics and chemistry:<br>` atomic mass unit (amu / Da / u) `,` planck mass `
- **Obsolete / Regional Units**<br>Historical or region-specific mass units no longer in widespread use:<br>` bale (cotton/wool/UK/AUS) `,` mark (Germany/Norway) `,` arroba (Spain/Portugal) `

**3. Temperature 🌡️**<br>
Unitflex includes a temperature converter that handles all major temperature scales with high accuracy, including both common and scientific units.
**Supported Units:**
- **Celsius (°C)**
- **Fahrenheit (°F)**
- **Kelvin (K)**
- **Réaumur (°Ré / °Re)**
- **Rankine (°R / °Ra)**

**4. Data 💾**<br>
Unitflex includes a robust data converter that supports a comprehensive range of digital storage and data rate units. From the tiniest bits to massive exabytes, this converter ensures accurate transformations across binary and decimal systems, ideal for IT, networking, and storage calculations.
**Supported Units:**
- **Basic Units**<br>Fundamental digital data measurements:<br>` bit `,` byte `,` nibble `
- **Decimal Units (SI Standard)**<br>Commonly used in storage devices and data plans, based on multiples of 1000:<br>` kilobyte (KB) `,` megabyte (MB) `,` gigabyte (GB) `,` terabyte (TB) `,` petabyte (PB) `,` exabyte (EB) `,` zettabyte(ZB) `,` yottabyte (YB) `
- **Binary Units (IEC Standard)**<br>Used in computing to represent exact binary multiples (base-1024):<br>` kibibyte (KiB) `,` mebibyte (MiB) `,` gibibyte (GiB) `,` tebibyte (TiB) `,` pebibyte (PiB) `,` exbibyte (EiB) `,` zebibyte (ZiB)`,` yobibyte (YiB) `
- **Bit-based Units**<br>Used especially for data transfer rates and bandwidth calculations:<br>` kilobit (kb) `,` megabit (Mb) `,` gigabit (Gb) `,` terabit (Tb) `,` petabit (Pb) `,` exabit (Eb) `,` zettabit (Zb) `,` Yottabit (Yb) `

> ⚠️ Case Sensitivity Notice:<br>The data converter in Unitflex is case-sensitive, following standard conventions:
> - Lowercase b stands for bit (e.g., Mb, Gb)
> - Uppercase B stands for byte (e.g., MB, GB)<br>Mixing cases (e.g., Gb vs GB) will yield very different results.

**5. Volume 💧**<br>
UnitFlex handles volume conversions across a wide spectrum, from tiny microliters to industrial oil barrels and large cubic yards. This module is ideal for scientific labs, culinary recipes, fluid mechanics, and everyday applications.
**Supported Units:**
- **Metric Units (SI)**<br>Standard international units for liquid and volumetric measurement, from nano- to kilometric scale:<br>` nanoliter (nl) `,` microliter (µl / μl) `,` milliliter (ml) `,` centiliter (cl) `,` deciliter (dl) `,` liter (l) `,` dekaliter (dal) `,` hectoliter (hl) `,` cubic millimeter (mm³) `,` cubic centimeter (cm³) `,` cubic decimeter (dm³) `,` cubic meter (m³) `,` cubic kilometer (km³) `
- **US Customary Units**<br>Commonly used in American cooking, fluid measurement, and household volume estimations:<br>` teaspoon (tsp) `,` tablespoon (tbsp) `,` fluid ounce (fl oz / floz) `,` cup, pint (pt) `,` quart (qt) `,` gallon (gal) `,` cubic inch (in³) `,` cubic foot (ft³) `,` cubic yard (yd³) `
- **UK Imperial Units**<br>Traditional British measurements, mainly used for larger volumes:<br>` imperial gallon (uk gal / uk-gal / gal-uk) `
- **Specialized Units**<br>Used in specific industries like oil and gas:<br>` barrel (bbl) `

**6. Pressure🧯**<br>
Unitflex supports comprehensive and precise pressure conversions across a wide range of scientific, engineering, meteorological, and industrial units. This module also features support for absolute vs gauge pressure calculations through the ` atmPressure ` parameter, enabling engineering-grade accuracy for systems that require contextual atmospheric pressure input (e.g., ` psia ` vs ` psig `)
**Supported Unit Categories:**
- **Metric Units (SI)**<br>Standard pascal-based units:<br>` pascal (Pa) `,` kilopascal (kPa) `,` megapascal (MPa) `,` gigapascal (GPa) `,` hectopascal (hPa) `
- **Bar & Millibar Units**<br>Common in meteorology and engineering:<br>` bar `,` millibar (mbar) `.
- **Atmospheric Pressure**<br>Standard atmospheric references:<br>` atmosphere (atm) `,` technical atmosphere (at) `
- **Torr & Mercury Units**<br>Used in vacuum measurements and medicine:<br>` torr `,` mmHg `,` inHg `
- **Pounds per Square Inch**<br>Widely used in industrial and automotive fields:<br>` psi `,` psia `,` psig `,` ksi `
- **CGS Units**<br>Centimeter-gram-second pressure units:<br>` barye `,` dyne/cm² `
- **Force-based Units**<br>Technical and traditional force/area units:<br>` kilogram-force per m² (kgf/m²) `,` kgf/cm²,ton-force per in² (tsi) `,` ton-force per ft² (tsf) `,` ton-force per m² (tf/m²) `
- **Pascal Fractions & Multiples**<br>Extreme values supported for scientific calculations:<br>` millipascal (mPa) `,` micropascal (μPa) `,` nanopascal (nPa) `,` picopascal (pPa) `,` terapascal (TPa) `,` exapascal (EPa) `

**Special Feature: psia / psig Conversion:**
This module includes support for converting between ` psia ` (pounds per square inch absolute) and ` psig ` (gauge), using the ` atmPressure ` parameter to specify the local atmospheric pressure.
``` python
from unitflex import pressure as press

# Convert 24 psig to psia with default atmospheric pressure (14.696 psi)
result = press.convert(24, "psig", "psia", prec=2, format="verbose", atmPressure=14.696)

# Convert back from psia to psig using custom atmospheric pressure
result = press.convert(38.7, "psia", "psig", atmPressure=14.7)
```
The default atmPressure is set to 14.696 psi, but you can customize this value to match local or experimental conditions for accurate conversions.


**7. Speed 🌀**<br> Unitflex includes an extensive speed converter that supports a wide array of velocity units, ranging from everyday measurements like kilometers per hour and miles per hour to scientific constants such as the speed of light. This module is ideal for applications in transportation, physics, engineering, and meteorology.
**Supported Units:**
- **Metric Units (SI)**<br>Standard international metric speed units:<br>` millimeter per second (mm/s) `,` centimeter per second (cm/s) `,` meter per second (m/s) `,` kilometer per hour (km/h) `
- **Imperial / US Customary Units**<br>Commonly used in the US, UK, and aviation:<br>` feet per second (ft/s) `,` inches per second (in/s) `,` miles per hour (mph) `,` knots (kt) `
- **Time Variants**<br>Conversions across different time bases:<br>` millimeter per minute (mm/min) `,` centimeter per minute (cm/min) `,` meter per minute (m/min) `,` inch per minute (in/min) `
- **Scientific & Relativistic Units**<br>Units used in high-speed and physics-related applications:<br>` mach (Ma) `,` speed of light (c) `

**8. Time ⏳**<br>
The unitflex time module ooffers extensive support for temporal unit conversions, from nanoseconds to millennia. Whether you're handling scientific timestamps, scheduling, calendar math, or historical durations, this module provides high precision, wide unit coverage, and human-readable breakdowns.
**Supported Units:**
- **Base Unit**<br>The standard SI base unit of time:<br>` second (s) `
- **Subsecond Units**<br>Units for very short time intervals, commonly used in computing and science:<br>` millisecond (ms) `,` microsecond (μs/us) `,` nanosecond (ns) `
- **Common Calendar Units**<br>Everyday time units from minutes to months:<br>` minute (min) `,` hour (h) `,` day (d) `,` week (w) `,` month (mo) `,` year (y) `.<br>Based on accurate average durations (e.g., 1 month = 30.44 days, 1 year = 365.25 days)
- **Expanded Calendar Units**<br>Additional terms based on academic or business periods:<br>` quarter `,` trimester `,` semester `,` bimonth `,` quadmester `
- **Extended Historical Units**<br>Used for longer timeframes in demographic, generational, or historical contexts:<br>` decade `,` score `,` generation `,` century `,` millennium `
- **Cultural / Regional Units**<br>Traditional units used in specific cultures or historical records:<br>windu,lustrum

**Special Feature: Time Duration Breakdown ` flex() `**: The ` flex() ` function allows you to break down a total duration into its most appropriate time units – from millennia to seconds – in a way that's easier for humans to read and interpret.
Unlike typical conversions that return a single target unit,` flex() ` recursively decomposes the total time (in any unit) into as many larger units as possible, stopping only when there's no remainder or the result is fully whole.
``` python
from unitflex import time

# Break down 123456789 seconds into human-readable time
print(time.flex(123456789, "second"))
# Output: "3 years 11 months 1 week 3 days 12 hours 34 minutes 49 seconds"

# Break down 500 days
print(time.flex(500, "day"))
# Output: "1 year 4 months 1 week 5 days"

# Custumize Range (optional)
print(time.flex(1.7832, "year", flexRange=("hour", "second")))
# Output: 15,631 hours 31 minutes 52 seconds

# Turning off delimiter by set delim to False (optional)
print(time.flex(1.7832, "year", flexRange=("hour", "second"), delim=False))
# Output: 15631 hours 31 minutes 52 seconds

# Works directly with convert function
print(time.flex(
    (time.convert(1.21231, "century", "day", mode="eng")), "day",
    flexRange=("month", "hour"),
    delim = False
    ))
# Output: 1454 months 3 weeks 2 days 11 hours


```
The ` flex() ` function is currently implemented for time, but the mechanism is designed to be extended to other domains (e.g., length, weight and data) that may benefit from breakdown representation.

> All units support both short and long forms.  
> The system automatically recognizes and converts them.

---

# Convert Function Parameters Explained 🔧
Each convert() function accepts up to six parameters. The first three are required, the rest are optional for customizing the output.

- **value (required)**<br>The numeric value to convert (int or float)<br>` Example: 100, 3.14 `

- **fromUnit (required)**<br>The original unit (short, long name, or symbol)<br>` Example: cm, meter, °f `

- **toUnit (required)**<br>The target unit (same format options as fromUnit)<br>` Example: km, yard, kelvin `

- **precision/prec/p (optional, default = 2 in standard mode and default = 9 in engineering mode)**<br>Number of decimal digits in the result<br>` Example: precision=3 → 12.345 `

- **format/fmt/f (optional, default = "raw")**<br> Output style:<br>` "raw" → numeric only (ideal for calculations) `<br>` "tag" → number + unit `<br>` verbose" → full expression (e.g. "1 meter = 100 cm")`

- **delimiter/delim/de (optional)**<br> Adds a separator:<br>` "default" or True → comma: 1,000,000 `<br>` "." → custom separator: 1.000.000 `<br>` False → no separator `
> ⚠️ **Note on delim and format="raw**<br>
>  When using format="raw", the output is intended for further calculations. Therefore, even if delim is set to "default" or any custom separator, no separators will be applied! the result will be returned as a clean float, int, or Decimal without formatting.

- **mode (optional, default = "standard")**<br>` "standard" → default mode `<br>` "engineering" → high-precision mode using decimal.Decimal `

**Convert Function Examples**
``` python
from unitflex import length as ln
# Basic Conversion
a = ln.convert(159, "cm", "ft")
# Output: 5.22

# Conversion Using Optional Paramter: (precision/prec/p)
b = ln.convert(1, "km", "miles", prec=5)
# Output: 0.62137

# Conversion Using Optional Parameter: (format/fmt/f)
c = ln.convert(1, "km", "miles", prec=5, fmt="raw")

# Conversion Using Optional Parameter: (delimiter/delim/de)
d = ln.convert(59800.6850, "km", "miles", prec=6, fmt="verbose", delim=True)
# Output: 59800.685 km = 37,158.422935 miles

# Conversion Using Optional Parameter: (mode/m) -> [mode="engineering"/"eng"/"e"]
e = ln.convert(1, "lightyear", "km", mode="eng", prec=12, fmt="verbose", delim=True)
# Output: 1 lightyear = 9,460,730,472,580.8000000000 km

```
---

# Notes 📌
- **Units are case-insensitive**, except for data storage units where` b `(bit) and` B `(byte) are different.
- **Input units must be unambiguous.** Avoid combining incompatible units or using unclear abbreviations.
- **Scientific and engineering accuracy:** Use ` mode="engineering" ` for precision-critical conversions (uses` decimal.Decimal `internally).
- **Highly precise with engineering mode using decimal, ideal for technical/scientific usage.**
- **Flexible unit names are supported** (e.g., "kg", "kilograms", "Kilogram"), but spelling mistakes won't be recognized.
- **Supports multiple output formats:** raw number, tag result (value + unit), or full verbose expression.
- **Output is rounded smartly by default**, you can override this behavior by setting prec or switching modes.
- **Some unit types require extra parameters** (e.g., pressure conversions from psig to psia need` atmPressure `defined).
- **Delimiters (like commas) are applied to large numbers** for easier readability unless raw mode is requested.

> ⚠️ **Note on Engineering Mode Output:**
> When using `mode="engineering"`, the result is returned as a high-precision `Decimal` object to ensure maximum accuracy.<br>Please note that `Decimal` values cannot be directly operated with `float` or `int` types in Python.

If you need to perform mathematical operations with the engineering mode result, consider casting it manually:
```python
float_result = float(result)
```
---

# Another Information 🔍
This library is now available on PyPI. You can install it directly using `pip install unitflex`. Once installed, you can import and use the unit classes from the unitflex package. Each class provides a convert() method that accepts the value to be converted, the source unit, the target unit, and other optional parameters.

After the installation with `pip install unitflex`, you can import and use this library by:<br>
```python
from unitflex import length, speed, time
 # Convert 12 mach to km/h
a = speed.convert(12, "mach", "km/h")

# Convert 18 years to seconds using delim, prec and format paramaters
b = time.convert(18.5, "year", "second", delim="default", prec=3, format="tag")

# Converting 12.0504 nanometers to centimeters using `engineering mode` to obtain a highly accurate result
c = length.convert(12.0504, "nm", "cm", format="raw", prec=12, mode="engineering")
```

The folder structure of this project is organized for clarity and scalability. The main package, `unitflex`, contains individual modules for each category of conversion (such as `length.py`, `mass.py`, `data.py`, `temperature.py ` and other modules unit). In addition, there are directories for usage examples and test scripts, which help demonstrate the library's capabilities and ensure consistent performance through future updates.

Upcoming features planned for unitflex include conversion of area, currency or even conversion with scientific units such as electricity, energy, power, force, luminous intensity, frequency, and more. While external contributions are currently limited as the library is in its early development stage, feedback and suggestions are more than welcome and encouraged.

Unitflex is released under the MIT License, which allows you to freely use, modify, and distribute the library as long as the original license is included. For more information about usage, structure, and licensing, please refer to the LICENSE file included in this repository.
