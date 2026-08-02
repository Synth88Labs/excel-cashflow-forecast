# Test Results — Excel Cash-Flow & Runway Forecaster

Full local test run + a live demo. CI re-runs the suite on Python 3.9, 3.11, 3.12.

## Unit tests

```
$ python -m pytest -v
tests/test_cashflow.py::test_active_monthly            PASSED
tests/test_cashflow.py::test_active_once               PASSED
tests/test_cashflow.py::test_active_quarterly          PASSED
tests/test_cashflow.py::test_active_end_month          PASSED
tests/test_cashflow.py::test_running_balance           PASSED
tests/test_cashflow.py::test_runway_detected           PASSED
tests/test_cashflow.py::test_once_and_quarterly_combine PASSED

======================= 7 passed =======================
```

**Result: 7/7 passed.**

### What each test proves
| Test | Verifies |
|---|---|
| `test_active_monthly` / `test_active_once` / `test_active_quarterly` | Each frequency activates in the right months |
| `test_active_end_month` | Items stop after their `end_month` |
| `test_running_balance` | Running balance accumulates net correctly |
| `test_runway_detected` | Runway = the first month the balance goes negative |
| `test_once_and_quarterly_combine` | Mixed one-off + recurring items combine correctly |

## Live demo (sample_data/cash_items.csv, opening balance 20,000)

```
$ python cashflow.py sample_data/cash_items.csv --start-balance 20000 --months 12

Cash-Flow & Runway Forecast
  Opening balance: 20,000   Horizon: 12 months
  Ending balance:  -8,200
  Lowest balance:  -8,200  (month 12)
  ** RUNWAY: cash goes negative in month 5 **
```

Projection:

| month | inflows | outflows | net | balance |
|---|---|---|---|---|
| 1 | 20000 | 17100 | 2900 | 22900 |
| 2 | 15000 | 20100 | -5100 | 17800 |
| 3 | 15000 | 20100 | -5100 | 12700 |
| 4 | 20000 | 28100 | -8100 | 4600 |
| **5** | 15000 | 20100 | -5100 | **-500** ← runway |
| 6 | 15000 | 20100 | -5100 | -5600 |
| … | | | | |
| 12 | 15000 | 17100 | -2100 | -8200 |

**Interpretation:** despite a healthy opening balance and profitable months, the
combination of a marketing push (months 2–6) and a month-4 tax bill drains cash — the
tool flags that the business **runs out of money in month 5**, months before it would be
obvious from the monthly P&L.
