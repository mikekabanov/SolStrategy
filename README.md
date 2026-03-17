# Sol Strategy - Trading Strategy Development

Python project for developing a self-correcting trading strategy for SOL-USDT pair targeting 30% monthly ROI.

## Project Structure

```
SolStrategy/
├── data/                    # Data files directory
│   └── moralis_sol_candles_feb.csv  # Input data
├── src/                     # Source modules
│   ├── data_loader.py       # Load and aggregate candles
│   ├── feature_engineering.py  # Calculate indicators
│   ├── labeling.py          # Label data and calculate metrics
│   ├── visualization.py     # Plotting utilities
│   └── __init__.py
├── notebooks/               # Jupyter notebooks for analysis
├── requirements.txt         # Python dependencies
└── README.md
```

## Step 1: Data Preparation

### 1.1 Load and Aggregate Data
- Load minute candles from CSV
- Create 5-minute candles
- Create hourly candles

### 1.2 Feature Engineering

Calculated for each dataset:

**Momentum Indicators:**
- RSI (14-period)

**Trend Indicators:**
- EMA (1-day period = 1440 minutes)
- EMA (10-day period = 14400 minutes)

**Derivatives:**
- First derivative (rate of change) for price and volume
- Second derivative (acceleration) for price and volume

**Additional Features:**
- Percentage price changes (1, 5, 15, 60 minute periods)
- Rolling volatility (20-period)
- High-Low range as % of close

### 1.3 Labeling

Identify profitable entry points by:
- Finding price increases of x% within n minutes
- Variable x and n for flexible labeling schemes
- Calculate for each entry point:
  - **max_roi_pct**: Maximum percentage gain within lookahead window
  - **time_to_max_roi_min**: Minutes to reach maximum ROI
  - **max_drawdown_pct**: Maximum loss percentage before reaching max ROI

### 1.4 Analysis

- Compare multiple labeling schemes
- Visualize most promising schemes
- Export labeled datasets for next stages

## Installation

```bash
pip install -r requirements.txt
```

## Usage

See `notebooks/` for analysis notebooks:
- `01_data_preparation.ipynb` - Load and explore data
- `02_feature_engineering.ipynb` - Calculate indicators
- `03_labeling_analysis.ipynb` - Label data and analyze
- `04_scheme_comparison.ipynb` - Compare labeling schemes

## Next Steps

- Step 2: Feature selection and validation
- Step 3: Model development (classification/regression)
- Step 4: Strategy backtesting and optimization
- Step 5: Risk management and position sizing
