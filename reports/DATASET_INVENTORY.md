# Uploaded dataset inventory and integration decisions

The project received 22 files. Several represent overlapping versions of the same daily case/death records, so the pipeline avoids adding them together: that would double-count the pandemic. Instead, one consistent country-day panel is used for the core forecasting experiment, with other sources catalogued as alternatives and cross-check candidates.

| File | Role in the project | Integration decision |
|---|---|---|
| `owid-covid-data.xlsx` | Daily country records plus population, demographic, health-system and policy context | Primary country-day panel; used in the main analysis and ML experiment |
| `country_wise_latest(1).csv` | Country-level cumulative snapshot | Alternate snapshot; not added to daily totals because dates/definitions may differ |
| `covid_19_clean_complete(1).csv` | Long-format daily country/province records | Secondary time-series source; use for source comparison, not aggregation with OWID |
| `day_wise(1).csv` | Global daily aggregates | Secondary aggregate source; useful for validation, not merged as extra countries |
| `full_grouped(1).csv` | Country-day grouped records | Secondary country-day source; overlaps with other time series |
| `usa_county_wise(1).csv` | Long-format US county/day records | Alternate county-level source; retained for detailed validation |
| `worldometer_data(1).csv` | Country snapshot with testing and population fields | Snapshot context; not combined with OWID cumulative totals |
| `covid_19_data.csv` | Long-format reported daily observations | Secondary time-series source; overlapping counts are not added to OWID |
| `time_series_covid_19_confirmed.csv` | Wide global cumulative confirmed counts | Alternate global source; dates run from 2020-01-22 to 2021-05-29 |
| `time_series_covid_19_confirmed_US.csv` | Wide US county cumulative confirmed counts | Used to create the US county snapshot |
| `time_series_covid_19_deaths.csv` | Wide global cumulative death counts | Alternate global source; dates run from 2020-01-22 to 2021-05-29 |
| `time_series_covid_19_deaths_US.csv` | Wide US county cumulative deaths and population | Used to create US county deaths and population-adjusted rates |
| `time_series_covid_19_recovered.csv` | Wide global recovered counts | Secondary source; recovery definitions are not directly comparable across providers |
| `population_by_country_2020(1).csv` | Country population reference | Joined by normalized country name for context and denominator checks |
| `countries_by_population_2019(1).csv` | Alternative 2019 population reference | Fallback population source if the 2020 file is absent |
| `country_codes_2020(1).csv` | Country identifiers | Reference for country harmonization |
| `country-and-continent-codes-list-csv(1).csv` | Country/continent mapping | Reference metadata for harmonization and Power BI geography |
| `2015(1).csv` | World Happiness Report | Joined as pre-pandemic context |
| `2016(1).csv` | World Happiness Report | Joined as pre-pandemic context |
| `2017(1).csv` | World Happiness Report | Joined as pre-pandemic context |
| `2018(1).csv` | World Happiness Report | Joined as pre-pandemic context |
| `2019(1).csv` | World Happiness Report | Joined as pre-pandemic context |

## Why use one primary daily panel?

The datasets have different shapes, update dates, geographic granularity, and reporting definitions. Summing across them would duplicate records and create invalid totals. The main country-level model therefore uses OWID consistently, happiness and population data enrich the country summary, and the US county files form a separate drill-down. The other overlapping sources remain documented as secondary sources for an explicit source-comparison extension.

The `source_inventory.csv` file records the detected row/column counts and date coverage for the uploaded files at the time this project was built.
