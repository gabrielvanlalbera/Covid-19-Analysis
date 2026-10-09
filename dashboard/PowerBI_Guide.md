# Power BI dashboard build guide

## Recommended report: Global COVID-19 Impact & Forecast Monitor

Use a dark navy background with white text, teal/blue for observed trends, orange for forecasts, and muted gray for context. Keep each page focused; avoid putting every chart on one canvas.

## Import these CSV files

Load the following from `data/processed/`:

1. `country_impact_summary.csv` — one row per country with latest available outcomes and enrichment indicators.
2. `country_daily_covid.csv` — daily trend data.
3. `forecast_test_predictions.csv` — actual future-window target and predictions on the holdout.
4. `forecast_model_metrics.csv` — model evaluation table.
5. `us_county_impact_summary.csv` — US county latest counts/rates.
6. `happiness_economic_covid_correlations.csv` — correlation matrix, useful for a matrix/heatmap rather than a fact table.

## Model relationships

- `country_impact_summary[country]` (one) → `country_daily_covid[location]` (many). If the country text differs for a small number of rows, use `iso_code` where possible or a separate country dimension table.
- Do not join the US county table to the global daily table by country name alone. Use it as a separate US detail page, with state/county fields.
- `forecast_test_predictions[location]` can relate to the country dimension, and `forecast_test_predictions[date]` can relate to a dedicated calendar table.

Create a calendar table in Power BI with `CALENDAR(MIN(country_daily_covid[date]), MAX(country_daily_covid[date]))`, mark it as the date table, and relate its date to the daily and forecast tables. Ensure CSV date fields are parsed as Date, not Text.

## Page 1 — Global overview

**Top KPI cards**
- Latest reported cumulative cases: sum of `total_cases_latest` from the country summary. Label this as the sum of country totals on each country's latest available date, because latest dates can differ.
- Latest reported cumulative deaths: sum of `total_deaths_latest` with the same date caveat.
- Countries in data: distinct count of `iso_code`.
- Latest date in the daily panel: max `date`.

**Visuals**
- Filled map: `country` or ISO code, color by `deaths_per_100k_latest` or `cases_per_100k_latest`.
- Line chart: `date` against daily new cases; use a 7-day average measure or a precomputed rolling series.
- Bar chart: top 10 countries by cases per 100,000 or deaths per 100,000.
- Slicers: continent, country, and date range.

Do not sum daily rows as if they were cumulative counts. Use `new_cases` for daily flow and `total_cases` for cumulative levels.

## Page 2 — Country comparison

- Scatter plot: happiness score vs deaths per 100,000; bubble size by population, legend by continent.
- Scatter plot: GDP per capita vs cases/deaths per 100,000.
- Bar chart: population-adjusted death burden by country.
- Add a note: associations are descriptive, confounded by age, testing, reporting, policy, health-system capacity, and epidemic timing.

## Page 3 — Forecast lab

- Line chart with `actual_next_7d_avg_cases_per_million` and selected `prediction_*` field by forecast origin date.
- Table/bar chart from `forecast_model_metrics.csv` with MAE, RMSE, R².
- Add a clear subtitle: “Historical holdout evaluation; predictions are daily new cases per million averaged over the following seven days.”
- Filter by country. Because the forecast test set is a specific historical window, label the dates prominently.

## Page 4 — US county deep dive

- Map: state/county location, color by `deaths_per_100k` or `cases_per_100k`.
- Top/bottom counties by population-adjusted burden; consider a minimum population threshold to avoid small-denominator volatility.
- Scatter: confirmed cases per 100k vs deaths per 100k, bubble size by population.
- Slicers: state and county.

## Suggested DAX measures

```DAX
Countries = DISTINCTCOUNT(country_impact_summary[iso_code])

Latest Data Date = MAX(country_daily_covid[date])

Average Country Death Rate per 100k =
AVERAGE(country_impact_summary[deaths_per_100k_latest])

Mean Forecast Absolute Error =
AVERAGE(forecast_model_metrics[MAE])
```

The “average country death rate” is an unweighted country average. For a population-weighted comparison, use totals with aligned dates and denominators instead.

## Polish checklist

- Use report tooltips to show the selected country, latest date, population, and per-capita metrics.
- Use consistent units in every title: counts, per 100,000 people, or per million people.
- Add a small “Data coverage & caveats” panel on each page.
- Use conditional formatting sparingly; reserve the strongest color for the main insight.
- Test interactions and map geocoding after publishing. Country names and county boundaries can require a geography dimension or shape map.
