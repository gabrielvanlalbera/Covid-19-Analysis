# Initial findings from the uploaded datasets

This report describes the first reproducible run. It is not a causal study and should be refreshed after adding later pandemic data.

## Coverage

- The primary daily panel contains **98,408 country-day rows across 220 countries**, covering **2020-01-01 to 2021-07-20**.
- Happiness indicators matched to **159 countries** after country-name normalization.
- The 2020 population reference matched **203 countries**.
- The US county table contains **3,342 geographic records**; the latest date in the supplied US county time-series files is **2021-05-29**.

## Forecasting experiment

The target is the average daily new reported cases per million over the following seven days. The time-based holdout uses 88,148 training rows and 4,202 test rows, with forecast origins from **2021-06-22 through 2021-07-13**.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Histogram-based Gradient Boosting | 14.39 | 37.34 | 0.945 |
| Random Forest | 15.62 | 48.48 | 0.907 |
| Seven-day rolling-mean baseline | 27.35 | 69.45 | 0.810 |

The gradient boosting model had the lowest MAE in this run. Its MAE of 14.39 means the average absolute error was about 14.39 reported new cases per million per day for the next-seven-day average target. The test is historical; this is not a live forecast for today's world.

## Early country-level comparisons

In the July 2021 OWID snapshot, Andorra, Seychelles, Montenegro, Bahrain, and Czechia were among the highest countries for recorded cumulative cases per million. Peru had the highest recorded cumulative deaths per million in this snapshot, followed by Hungary and Bosnia and Herzegovina. Small countries can have volatile per-capita rates, and confirmed cases depend heavily on testing and reporting practices.

## Happiness and recorded pandemic burden

For countries with matched happiness and COVID-19 data (158 complete pairs in the pairwise correlation), the Pearson correlation between pre-pandemic average happiness score and recorded cumulative cases per 100,000 was approximately **+0.52**; the correlation with recorded cumulative deaths per 100,000 was approximately **+0.36**. The happiness GDP component was also positively correlated with recorded cases per 100,000 in this sample (about **+0.61**).

These positive correlations must not be interpreted as evidence that happiness or wealth increased COVID-19 transmission or deaths. Higher-income countries often have different testing access, age structures, travel patterns, reporting completeness, epidemic timing, and healthcare systems. The next stage should use multivariable analysis and sensitivity checks, and should clearly distinguish recorded burden from true infection burden.

## US county detail

Population-normalized county rates are calculated only when the supplied population is positive and available. For an interpretable comparison, the dashboard should allow a minimum population filter because rates for small or special-purpose county records can be unstable. County-level records end on 2021-05-29, earlier than the primary global panel.

For the US county comparison, using only counties with population at least 100,000 to reduce small-denominator volatility, Navajo County (Arizona), Bronx and Queens (New York), Imperial County (California), and Kings County (New York) were among the highest by recorded deaths per 100,000 in the supplied May 2021 snapshot. This is a snapshot ranking, not a statement about current county conditions.

## Key limitation

The primary global workbook stops on **2021-07-20**. The current project can analyze the first pandemic waves and early vaccination period represented in the files, but it cannot credibly claim to measure long-term post-pandemic effects through 2022–2025. Add later data before making those claims.
