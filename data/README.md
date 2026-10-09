# Data folder

## Raw files

Place the original downloaded datasets in `data/raw/`. The pipeline intentionally does not commit raw source datasets: several files are large, overlapping, and governed by their source providers' terms. The processed Power BI exports are committed under `data/processed/` for transparency and ease of use.

The primary daily country panel is `owid-covid-data.xlsx` (Our World in Data export). Optional enrichment files supported by the pipeline include:

- `2015(1).csv` through `2019(1).csv` — World Happiness Report country indicators
- `population_by_country_2020(1).csv` or `countries_by_population_2019(1).csv` — population references
- `time_series_covid_19_confirmed_US.csv` — US county confirmed counts
- `time_series_covid_19_deaths_US.csv` — US county death counts

Other uploaded COVID-19 files are valuable cross-checks and alternate source views, but the core pipeline uses one primary country-time panel to avoid double-counting records from overlapping datasets.

## Processed outputs

- `country_daily_covid.csv`: country-day observations for trend analysis
- `country_impact_summary.csv`: latest available country indicators and derived rates
- `happiness_economic_covid_correlations.csv`: descriptive correlation matrix
- `us_county_impact_summary.csv`: latest US county cumulative counts and per-capita rates
- `forecast_model_metrics.csv`: held-out time-based model evaluation
- `forecast_test_predictions.csv`: held-out actuals, baseline, and model predictions
- `run_summary.json`: metadata about the run and data coverage
- `source_inventory.csv`: inventory of the 22 uploaded source files and their date coverage
