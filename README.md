# Excel Cash-Flow & Runway Forecaster 💵

[![CI](https://github.com/Synth88Labs/excel-cashflow-forecast/actions/workflows/ci.yml/badge.svg)](https://github.com/Synth88Labs/excel-cashflow-forecast/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

List your recurring inflows and outflows and get a **month-by-month cash-flow
projection** — with the running balance and, most importantly, your **runway**: the
month your cash would run out.

Built for the question every founder and small-business owner loses sleep over:
*"Will I make payroll — and how many months do I have?"*

## What it does

- Projects **inflows, outflows, net, and running balance** for each month
- Flags your **runway** — the first month the balance goes negative
- Reports the **lowest point** (and which month) so you can see the crunch coming
- Handles **once / monthly / quarterly** items with optional end dates

## The input file

A simple CSV of cash items:

```
name,type,amount,start_month,frequency,end_month
Product sales,inflow,15000,1,monthly,
Consulting,inflow,5000,1,quarterly,
Payroll,outflow,14000,1,monthly,
Marketing push,outflow,3000,2,monthly,6
Tax bill,outflow,8000,4,once,
```

- **type**: `inflow` or `outflow`
- **frequency**: `once`, `monthly`, or `quarterly`
- **end_month**: optional (blank = runs to the end of the horizon)

## Installation

```bash
git clone https://github.com/Synth88Labs/excel-cashflow-forecast.git
cd excel-cashflow-forecast
pip install -r requirements.txt
```

Requires Python 3.9+.

## Usage

```bash
python cashflow.py <items.csv> --start-balance N --months N [-o projection.csv]
```

### Quick start (try it on the included sample)

```bash
python cashflow.py sample_data/cash_items.csv --start-balance 20000 --months 12
```

Example output:

```
Cash-Flow & Runway Forecast
  Opening balance: 20,000   Horizon: 12 months
  Ending balance:  ...
  Lowest balance:  ...  (month ...)
  ** RUNWAY: cash goes negative in month 5 **
```

…plus a `month, inflows, outflows, net, balance` file you can chart.

### Options

| Option | Description |
|---|---|
| `--start-balance N` | **Required.** Opening cash balance |
| `--months N` | Months to project. Default: 12 |
| `-o`, `--output` | Output path (`.csv` or `.xlsx`) |
| `--sheet NAME` | For Excel input, a specific sheet |

## Test results

See [TEST_RESULTS.md](TEST_RESULTS.md), or run them yourself:

```bash
pip install pytest
python -m pytest
```

## 📚 Learn More — Free Excel Tutorials

Practical Excel, budgeting & forecasting guides at
**[ExcelGuru.io](https://excelguru.io/category/tutorials/)**.

## License

MIT — see [LICENSE](LICENSE).
