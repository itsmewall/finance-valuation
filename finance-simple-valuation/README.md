# Finance Simple Valuation

A simplified Python project for financial valuation (DCF) using CSV data and minimal dependencies.
Built for educational purposes to demonstrate a clean, modular pipeline.

## Installation

1. **Clone the repository** (if applicable) or download the source.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install pandas numpy matplotlib streamlit pydantic
   # OR
   pip install -e .
   ```

## Usage

### Run the Valuation Pipeline
To process data, calculate metrics, run DCF scenarios, and generate outputs:
```bash
python run.py
```
This will:
- Read CSVs from `data/`
- validate data
- Calculate historical FCF
- Project 5 years for Base/Downside/Upside scenarios
- Export results to `outputs/`

### View the Dashboard
To visualize the results (Valuation Summary, Projections, Sensitivity Heatmap):
```bash
streamlit run app.py
```

## Project Structure

- `run.py`: Main entry point to execute the pipeline.
- `config.py`: Configuration settings (wacc, growth rates, assumptions).
- `app.py`: Streamlit dashboard for viewing results.
- `data/`: Folder containing input CSVs (Income Statement, Balance Sheet, Cash Flow).
- `outputs/`: Generated results (summary.json, projections.csv, sensitivity.png).
- `src/`: Source code modules (io, finance, reporting, pipeline).
- `tests/`: Unit tests.

## Disclaimer

This is a **simplified model** for study and demonstration purposes. It uses basic assumptions (e.g., constant margins, simplified NWC) and is **NOT** a financial recommendation.
