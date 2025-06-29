# Flat Price Predictor

Flat Price Predictor is an end-to-end pipeline that scrapes Wrocław flat listings, tags them with districts, and trains machine learning models to estimate sale prices.

## Features

- **Web Scraping**: Scrape property listings from [otodom.pl](https://www.otodom.pl) using `scraper.py`.
- **Geospatial Classification**: Map each property to its Wrocław district using `geoposition.py` (GeoPandas).
- **Price Prediction**: Clean the data, engineer features, and train regression models in `flat-predictor.ipynb` (scikit-learn).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flat-price-predictor.git
   cd flat-price-predictor
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Scrape Listings

Run the scraper to collect listings data:

```bash
python scraper.py [-l N] [-f <output_file>]
```

- `-l, --listings N`: Number of scraped listings (default: all pages).
- `-f, --file`: Save data to a custom CSV file (default: `temp.csv`).

### 2. Price Prediction Notebook

Launch JupyterLab and open the notebook:

```bash
jupyter lab flat-predictor.ipynb
```
