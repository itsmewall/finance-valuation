# Finance Simple Valuation (Batch Pipeline)

A pure Python pipeline for financial valuation (DCF) using CSV data.
Generates deterministic outputs (JSON, CSV, PNG) without any web interface.

## Installation

1. **Clone the repository** (if applicable).
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install pandas numpy matplotlib pydantic
   # OR
   pip install -e .
   ```

## Usage

### Run the Pipeline
Execute the main script to process data and generate reports:
```bash
python run.py
```

This will:
1. Load income statement, balance sheet, and cash flow CSVs from `data/`.
2. Validate data consistency (years, columns).
3. Project financials for 5 years (Base/Downside/Upside scenarios).
4. Run DCF valuation for each scenario.
5. Perform sensitivity analysis (WACC vs Terminal Growth).
6. Export all results to `outputs/`.

## Outputs

All generated files are located in the `outputs/` directory:

- `summary.json`: Comprehensive valuation results including Enterprise Value, Equity Value, and key assumptions for each scenario.
- `projections.csv`: Year-by-year projected financials (Revenue, EBIT, FCF, etc.) for all scenarios.
- `sensitivity_ev.csv`: Matrix of Enterprise Values across different WACC and Terminal Growth rates.
- `sensitivity.png`: Heatmap visualization of the sensitivity analysis.
- `run_log.txt`: Detailed execution log with timestamps.

## Configuration

Settings are defined in `config.py`. You can adjust:
- **Scenarios**: Growth rates, margins, WACC, etc. for Base, Downside, and Upside.
- **Sensitivity Grid**: Range of WACC and Terminal Growth values.
- **Global Params**: Tax rate, forecast years, etc.

## Structure

- `run.py`: Entry point.
- `config.py`: Central configuration.
- `src/`: Core logic modules.
  - `pipeline/`: Orchestration.
  - `finance/`: DCF, projections, metrics.
  - `io/`: Data loading and validation.
  - `reporting/`: Export logic.
- `data/`: Input CSV files.

## Disclaimer

This is a simplified valuation model for educational purposes. It relies on provided assumptions and input data. Not financial advice.
