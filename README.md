# Florence Airbnb Dashboard

Interactive Streamlit + Altair dashboard built on the Inside Airbnb dataset for Florence, Italy.

## Files in this repo
- `app.py` — the Streamlit dashboard
- `listings.csv` — the Florence Inside Airbnb data
- `requirements.txt` — Python dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud (free, gives you a shareable link)

1. Push these three files to a **public GitHub repo** (e.g. `florence-airbnb-dashboard`).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app** → pick your repo, branch `main`, main file `app.py`.
4. Click **Deploy**. After ~2 minutes you get a URL like `https://florence-airbnb-dashboard.streamlit.app` — that's what you submit.

## What the dashboard does
- **Sidebar filters**: neighborhood multiselect, room-type multiselect, price-range slider, minimum-reviews slider. All four filters apply to every chart simultaneously.
- **KPI strip**: live counts and averages that update with the filters.
- **Chart 1 — Listings by neighborhood** (bar)
- **Chart 2 — Price distribution by room type** (boxplot)
- **Chart 3 + 4 — Price vs. review score scatter + linked histogram**: drag a box on the scatter to filter the histogram beneath it (Altair-native cross-chart brushing).
- **Map** of the filtered listings using lat/long.
- **Expandable raw-data table** for inspection.
