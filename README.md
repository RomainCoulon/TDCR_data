# TDCR Data

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A repository dedicated to processing, standardizing, and analyzing **Triple-to-Double Coincidence Ratio (TDCR)** data for liquid scintillation counting and radionuclide metrology.

---

## Overview

The **TDCR method** is a primary standardisation technique used in radionuclide metrology to calculate the detection efficiency of liquid scintillation counters without needing a reference source. 

This repository provides tools, scripts, and benchmark data structures to:
- Parse raw TDCR coincidence counter outputs (e.g., $N_A, N_B, N_C, N_D, N_T$).
- Calculate experimental TDCR ratios ($K = T/D$).
- Evaluate measurement uncertainties and dead-time corrections.
- Standardize data formats for reproducibility across laboratory experiments.

---

## Directory Structure

```text
TDCR_data/
├── data/
│   ├── raw/          # Raw counter output files
│   └── processed/    # Cleaned, standardized datasets
├── notebooks/        # Jupyter notebooks for data analysis & visualization
├── src/
│   ├── parser.py     # Data ingestion and format conversions
│   ├── tdcr.py       # Core TDCR ratio and efficiency calculations
│   └── utils.py      # Helper utilities
├── tests/            # Unit tests
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/RomainCoulon/TDCR_data.git
cd TDCR_data
pip install -r requirements.txt
```

---

## Quick Start

```python
from src.tdcr import calculate_tdcr

# Input raw coincidence counts (Triples, Doubles)
triples = 12450
doubles = 12890

# Calculate TDCR ratio
tdcr_ratio = calculate_tdcr(triples, doubles)
print(f"Experimental TDCR ratio (K): {tdcr_ratio:.4f}")
```

To run example data processing pipelines:

```bash
python src/parser.py --input data/raw/sample_measurement.csv --output data/processed/
```

---

## Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add NewFeature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
