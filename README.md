# Daily QQQ/SPY PE Tracker

This repo uses GitHub Actions to fetch QQQ and SPY PE data from Yahoo Finance daily and append to `data/pe_history.csv`.

## Run locally

```bash
pip install -r requirements.txt
python src/fetch_pe.py

