# COVID-19 Global Impact & Forecasting Analytics

**A reproducible data analytics and machine learning project connecting COVID-19 trends, population-adjusted outcomes, pre-pandemic happiness/economic indicators, and US county-level differences.**

This project is designed for a portfolio: the analysis is explainable, the model is evaluated on a time-based holdout, the outputs are ready for Power BI, and the limitations are documented instead of hidden.

## Questions this project explores

1. How did reported COVID-19 cases and deaths change over time across countries?
2. Which countries had the highest reported burden after accounting for population?
3. How different were the outcomes across US counties?
4. Are pre-pandemic happiness and economic indicators associated with later reported COVID-19 outcomes?
5. Can daily country-level case rates help forecast the average daily case rate over the following seven days?

These are observational questions. Correlation does not show that economic conditions or happiness caused a particular pandemic outcome.

## What is included

- **Country-day panel:** 98,408 country-day records, 220 countries, from 2020-01-01 to 2021-07-20 in the uploaded Our World in Data workbook.
- **Country impact table:** latest available cumulative counts, population-normalized rates, demographic/economic indicators, and joined pre-pandemic happiness indicators where names match.
- **US county summary:** county-level confirmed/death counts and population-normalized rates from the uploaded US time-series files.
- **Forecasting experiment:** seven-day-ahead average daily new cases per million, compared against a simple rolling-average baseline and two ML models.
- **Power BI exports and guide:** prepared CSV tables, suggested report pages, KPI definitions, interactions, and a dashboard theme.
- **Figures:** global trend, per-capita country ranking, and forecast-vs-actual examples.
- **Dataset provenance:** an inventory of all 22 uploaded files and the reason overlapping sources are kept separate.

Raw data files are not included because the uploaded source files are large and several overlap. The processed outputs are included so the analysis and dashboard can be explored immediately. To rerun the full pipeline from scratch, place the original files in `data/raw/` as described in [`data/README.md`](data/README.md).

## Quick start

### 1. Create an environment

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the analysis

Copy `owid-covid-data.xlsx` and any optional enrichment files into `data/raw/`, then run from the repository root:

```bash
python src/run_analysis.py --raw-dir data/raw --output-dir data/processed
```

The pipeline creates processed tables, model metrics, a held-out prediction table, figures, a run summary, and serialized models under `models/`.

### 3. Explore the notebook

Open `notebooks/01_covid_global_impact.ipynb` in Jupyter or VS Code. It reads the included processed tables and reproduces the main exploratory views.

### 4. Build the Power BI report

Follow [`dashboard/PowerBI_Guide.md`](dashboard/PowerBI_Guide.md), import the processed CSVs, set up the relationships, and use `dashboard/covid_theme.json` as the report theme.

## Modeling design

### Target

`target_next_7d_avg_cases_per_million` is the average daily new reported cases per million people over the **next seven days** for each country, using only country/date rows for which the full target window exists.

### Predictors

- Lagged case rates: 1, 7, 14, and 21 days
- Previous 7-, 14-, and 28-day rolling means
- Calendar month and day-of-year
- Population and available country-level indicators such as GDP per capita, median age, life expectancy, hospital beds, HDI, stringency index, and reproduction rate

Rolling features are shifted so they use prior observations, not the target window. A chronological holdout is used rather than a random row split. The latest eligible dates are held out for evaluation.

### Models and evaluation

- **Baseline:** previous seven-day rolling average
- **Random Forest Regressor**
- **Histogram-based Gradient Boosting Regressor**

Metrics: MAE, RMSE, and R². MAE/RMSE are in **daily new reported cases per million**, not absolute cases. The test set is a historical holdout, not proof that the model will generalize to a future variant, policy environment, or different surveillance system.

## Initial model results

The initial run on the uploaded workbook used 88,148 training rows and 4,202 test rows. The eligible test forecast origins ran from 2021-06-22 through 2021-07-13.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Histogram-based Gradient Boosting | 14.39 | 37.34 | 0.945 |
| Random Forest | 15.62 | 48.48 | 0.907 |
| 7-day rolling mean baseline | 27.35 | 69.45 | 0.810 |

These are the results from the current run; they should be re-evaluated after any data or feature changes. Large differences between countries, under-reporting, and revisions in reported counts can affect the metrics.

## Important data limitations

- The uploaded OWID workbook ends on **2021-07-20**, so this version cannot measure long-term effects several years after the pandemic without additional later data.
- Reported cases are not the same as all infections; testing access and reporting practices vary by country and date.
- Population-adjusted cumulative case rates can exceed 100,000 per 100,000 in some small countries because repeat infections and reporting definitions differ; interpret them as reported cumulative case events, not the share of unique residents infected.
- Happiness reports are from 2015–2019 and their column definitions vary slightly by edition. Joined results are descriptive and only available for matched country names.
- Country-level relationships should not be used to infer individual-level effects (ecological fallacy).
- US county rates may be unstable for small populations and the supplied county files can have reporting differences or suppressed/missing county data.
- A forecast is a statistical estimate, not public-health advice.

## Repository layout

```text
covid-global-impact-ml/
├── data/
│   ├── raw/                         # add original source files here
│   ├── processed/                   # report-ready CSVs included
│   └── README.md
├── dashboard/
│   ├── PowerBI_Guide.md
│   └── covid_theme.json
├── models/                          # trained models generated by pipeline
├── notebooks/
│   └── 01_covid_global_impact.ipynb
├── reports/
│   ├── INITIAL_FINDINGS.md
│   └── figures/
├── src/
│   └── run_analysis.py
├── requirements.txt
└── README.md
```

## Data provenance

The workbook is an Our World in Data COVID-19 dataset export. Other optional files are the country-level and US county-level COVID-19 time series and World Happiness Report tables supplied for this project. Check the source pages and dataset-specific licenses before redistributing source data. This repository does not claim ownership of the original datasets.

## Suggested GitHub description

> Country-level COVID-19 impact analytics with population-adjusted comparisons, happiness/economic context, US county analysis, time-aware ML forecasting, and Power BI-ready reporting tables.

## Next improvements

- Add later pandemic and post-pandemic data to assess longer-run outcomes.
- Add rolling-origin backtesting and evaluate performance separately by region and incidence level.
- Include vaccination and testing indicators only where coverage is adequate and definitions are consistent.
- Build a Power BI tooltip page for country context and a drill-through page for US states/counties.
