# Global Energy Market Analysis

A data analysis pipeline for market sizing and competitive benchmarking across the global energy sector.

## Overview

This tool analyzes 20 energy companies across 6 regions and 5 sectors (Oil & Gas, Renewables, Utilities, Nuclear, Energy Storage, Coal) to provide:

- **Market sizing** by sector and region
- **Growth analysis** identifying fastest-growing companies
- **Sustainability scoring** based on renewable mix, carbon intensity, and R&D investment
- **Competitive positioning** within sectors

## Project Structure

```
├── data/                    # Raw datasets
│   └── global_energy_market.csv
├── src/                     # Core pipeline
│   ├── data_loader.py       # Data loading, validation, cleaning
│   ├── analysis.py          # Market sizing & benchmarking logic
│   └── api.py               # FastAPI REST endpoints
├── tests/                   # Test suite
│   ├── test_analysis.py     # Analysis unit tests
│   └── test_api.py          # API endpoint tests
├── notebooks/               # Interactive analysis
│   └── market_analysis.ipynb
└── requirements.txt
```

## Quick Start

```bash
pip install -r requirements.txt
pytest tests/
uvicorn src.api:app --reload
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/market-size` | Market size breakdown by sector |
| `GET /api/regional-benchmark` | Regional benchmarking |
| `GET /api/growth-leaders?top_n=5` | Top growing companies |
| `GET /api/sustainability` | Sustainability scores |
| `GET /api/competitive/{sector}` | Competitive positioning |
| `GET /api/company/{name}` | Company detail |
| `GET /api/compare?sector_a=X&sector_b=Y` | Sector comparison |

## Known Issues

There are a few bugs in the codebase that need to be fixed — run `pytest` to see failing tests.
