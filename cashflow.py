"""
cashflow.py — Excel Cash-Flow & Runway Forecaster.

Turn a list of recurring inflows and outflows into a month-by-month cash-flow
projection — with the running balance and, crucially, your **runway**: the month
your cash would run out.

Input is a simple CSV of cash items:

    name,type,amount,start_month,frequency,end_month
    Product sales,inflow,15000,1,monthly,
    Payroll,outflow,14000,1,monthly,
    Tax bill,outflow,8000,4,once,

    type      : inflow | outflow
    frequency : once | monthly | quarterly
    end_month : optional (blank = runs to the end of the horizon)

Usage:
    python cashflow.py <items.csv> --start-balance N --months N [-o projection.csv]

Author: Synth88Labs
License: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def read_items(path: Path, sheet: str | None) -> list[dict]:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    else:
        df = pd.read_excel(path, sheet_name=sheet if sheet is not None else 0, dtype=str, na_filter=False)
    required = {"name", "type", "amount", "start_month", "frequency"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing column(s): {', '.join(sorted(missing))}. "
                         f"Need: name, type, amount, start_month, frequency [, end_month].")
    items = []
    for _, row in df.iterrows():
        typ = str(row["type"]).strip().lower()
        if typ not in ("inflow", "outflow"):
            raise ValueError(f"Row '{row['name']}': type must be 'inflow' or 'outflow', got '{typ}'.")
        freq = str(row["frequency"]).strip().lower()
        if freq not in ("once", "monthly", "quarterly"):
            raise ValueError(f"Row '{row['name']}': frequency must be once/monthly/quarterly.")
        end = str(row.get("end_month", "")).strip()
        items.append({
            "name": row["name"], "type": typ,
            "amount": float(row["amount"]),
            "start": int(float(row["start_month"])),
            "freq": freq,
            "end": int(float(end)) if end else None,
        })
    return items


def is_active(item: dict, month: int) -> bool:
    if month < item["start"]:
        return False
    if item["end"] is not None and month > item["end"]:
        return False
    if item["freq"] == "once":
        return month == item["start"]
    if item["freq"] == "monthly":
        return True
    if item["freq"] == "quarterly":
        return (month - item["start"]) % 3 == 0
    return False


def project(items: list[dict], start_balance: float, months: int) -> dict:
    rows = []
    balance = start_balance
    runway = None       # first month balance goes negative
    lowest = (start_balance, 0)
    for m in range(1, months + 1):
        inflow = sum(it["amount"] for it in items if it["type"] == "inflow" and is_active(it, m))
        outflow = sum(it["amount"] for it in items if it["type"] == "outflow" and is_active(it, m))
        net = inflow - outflow
        balance += net
        rows.append({"month": m, "inflows": round(inflow, 2), "outflows": round(outflow, 2),
                     "net": round(net, 2), "balance": round(balance, 2)})
        if balance < lowest[0]:
            lowest = (balance, m)
        if runway is None and balance < 0:
            runway = m
    return {"rows": rows, "ending_balance": balance, "runway": runway,
            "lowest_balance": lowest[0], "lowest_month": lowest[1]}


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Forecast monthly cash flow and runway from a list of cash items.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path, help="CSV/XLSX of cash items.")
    p.add_argument("--start-balance", type=float, required=True, help="Opening cash balance.")
    p.add_argument("--months", type=int, default=12, help="Months to project. Default: 12")
    p.add_argument("-o", "--output", type=Path, default=None, help="Output path (.csv or .xlsx).")
    p.add_argument("--sheet", default=None, help="For Excel input: sheet name (default: first).")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if not args.input.is_file():
        print(f"Error: '{args.input}' is not a file.", file=sys.stderr)
        return 1
    try:
        items = read_items(args.input, args.sheet)
        result = project(items, args.start_balance, args.months)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    out = pd.DataFrame(result["rows"])
    out_path = args.output or args.input.with_name(f"{args.input.stem}_projection.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".csv":
        out.to_csv(out_path, index=False)
    else:
        out.to_excel(out_path, index=False, sheet_name="CashFlow")

    print("Cash-Flow & Runway Forecast")
    print(f"  Opening balance: {args.start_balance:,.0f}   Horizon: {args.months} months")
    print(f"  Ending balance:  {result['ending_balance']:,.0f}")
    print(f"  Lowest balance:  {result['lowest_balance']:,.0f}  (month {result['lowest_month']})")
    if result["runway"] is not None:
        print(f"  ** RUNWAY: cash goes negative in month {result['runway']} **")
    else:
        print(f"  Runway: cash stays positive for all {args.months} months.")
    print(f"\nSaved: {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
