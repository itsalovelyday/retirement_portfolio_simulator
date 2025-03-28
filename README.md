# Retirement Portfolio Simulator

A web-based retirement portfolio simulator built with Dash and Plotly. This application helps users visualize and analyze their retirement savings growth through Monte Carlo simulations.

## Features

- Interactive portfolio growth simulations
- Monte Carlo analysis with multiple scenarios
- Real-time statistics and projections
- Customizable parameters:
  - Starting age
  - Retirement age
  - Monthly income and expenses
  - Expected returns and volatility
  - Inflation rate
  - Initial investment
- Visual representation of portfolio growth
- Retirement statistics including:
  - Average portfolio value
  - Median portfolio value
  - 10th and 90th percentiles
  - Expected monthly investment income

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd retirement
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/MacOS
```

3. Install dependencies:
```bash
pip install dash plotly pandas numpy
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:8050
```

3. Adjust the parameters in the sidebar and click "Run Simulation" to see the results.

## Dependencies

- dash
- plotly
- pandas
- numpy

## License

MIT License 