from __future__ import annotations

import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf


SYMBOLS = ["QQQ", "SPY"]
OUT_CSV = os.path.join("data", "pe_history.csv")


def safe_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def fetch_pe(symbol: str) -> tuple[float | None, float | None]:
    """
    Return (trailing_pe, forward_pe) from Yahoo via yfinance.
    For ETFs, these fields may sometimes be missing -> None.
    """
    t = yf.Ticker(symbol)
    info = t.info or {}
    trailing = safe_float(info.get("trailingPE"))
    forward = safe_float(info.get("forwardPE"))
    return trailing, forward


def main() -> None:
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)

    now_utc = datetime.now(timezone.utc)
    run_ts_utc = now_utc.replace(microsecond=0).isoformat()

    ny_tz = ZoneInfo("America/New_York")
    asof_date_ny = now_utc.astimezone(ny_tz).date().isoformat()

    rows = []
    for sym in SYMBOLS:
        trailing_pe, forward_pe = fetch_pe(sym)
        rows.append(
            {
                "run_ts_utc": run_ts_utc,
                "asof_date_ny": asof_date_ny,
                "symbol": sym,
                "trailing_pe": trailing_pe,
                "forward_pe": forward_pe,
            }
        )

    new_df = pd.DataFrame(rows)

    # Append, but avoid duplicate (same asof_date_ny + symbol)
    if os.path.exists(OUT_CSV):
        old_df = pd.read_csv(OUT_CSV)
        merged = pd.concat([old_df, new_df], ignore_index=True)

        merged = merged.drop_duplicates(subset=["asof_date_ny", "symbol"], keep="last")
        merged = merged.sort_values(["asof_date_ny", "symbol"]).reset_index(drop=True)
    else:
        merged = new_df

    merged.to_csv(OUT_CSV, index=False)
    print(f"Saved {len(new_df)} rows. Total rows now: {len(merged)}")
    print(new_df.to_string(index=False))


if __name__ == "__main__":
    main()
