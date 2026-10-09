"""Build reproducible country-level COVID-19 analysis and Power BI exports.

The pipeline uses Our World in Data as the primary daily country panel, merges
pre-pandemic World Happiness indicators and population references when possible,
and creates a separate US county-level snapshot. Raw data are not bundled with
this repository; see data/README.md for expected filenames and provenance.
"""
from __future__ import annotations
import argparse
import json
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

ALIASES = {
    "united states": "united states", "united states of america": "united states",
    "us": "united states", "usa": "united states", "south korea": "south korea",
    "korea, south": "south korea", "korea, republic of": "south korea",
    "russia": "russia", "russian federation": "russia", "iran": "iran",
    "iran, islamic republic of": "iran", "venezuela": "venezuela",
    "venezuela, bolivarian republic of": "venezuela", "tanzania": "tanzania",
    "united republic of tanzania": "tanzania", "bolivia": "bolivia",
    "bolivia, plurinational state of": "bolivia", "moldova": "moldova",
    "moldova, republic of": "moldova", "laos": "laos",
    "lao people's democratic republic": "laos", "syria": "syria",
    "syrian arab republic": "syria", "brunei": "brunei",
    "brunei darussalam": "brunei", "czech republic": "czechia",
    "czechia": "czechia", "ivory coast": "cote d'ivoire",
    "cote d'ivoire": "cote d'ivoire", "taiwan*": "taiwan",
    "taiwan": "taiwan", "palestine": "palestine", "state of palestine": "palestine",
    "hong kong": "hong kong", "macau": "macao", "cape verde": "cabo verde",
    "swaziland": "eswatini", "burma": "myanmar", "micronesia": "micronesia",
    "kosovo": "kosovo", "north macedonia": "north macedonia",
    "the bahamas": "bahamas", "bahamas": "bahamas", "gambia": "gambia",
    "the gambia": "gambia", "congo (brazzaville)": "congo",
    "congo (kinshasa)": "democratic republic of congo",
    "democratic republic of the congo": "democratic republic of congo",
    "republic of the congo": "congo", "kyrgyz republic": "kyrgyzstan",
    "slovak republic": "slovakia", "turkiye": "turkey", "turkey": "turkey",
    "egypt, arab rep.": "egypt", "egypt": "egypt", "yemen, rep.": "yemen",
}

def country_key(value) -> str:
    if pd.isna(value):
        return ""
    s = str(value).strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = ALIASES.get(s, s)
    return s

def find_file(raw: Path, candidates: list[str]) -> Path | None:
    for name in candidates:
        p = raw / name
        if p.exists():
            return p
    return None

def safe_numeric(df: pd.DataFrame, cols: list[str]) -> None:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

def load_happiness(raw: Path) -> pd.DataFrame:
    candidates = [
        ("2015(1).csv", "Country", "Happiness Score", "Economy (GDP per Capita)", "Health (Life Expectancy)", "Family", "Freedom", "Trust (Government Corruption)", "Generosity"),
        ("2016(1).csv", "Country", "Happiness Score", "Economy (GDP per Capita)", "Health (Life Expectancy)", "Family", "Freedom", "Trust (Government Corruption)", "Generosity"),
        ("2017(1).csv", "Country", "Happiness.Score", "Economy..GDP.per.Capita.", "Health..Life.Expectancy.", "Family", "Freedom", "Trust..Government.Corruption.", "Generosity"),
        ("2018(1).csv", "Country or region", "Score", "GDP per capita", "Healthy life expectancy", "Social support", "Freedom to make life choices", "Perceptions of corruption", "Generosity"),
        ("2019(1).csv", "Country or region", "Score", "GDP per capita", "Healthy life expectancy", "Social support", "Freedom to make life choices", "Perceptions of corruption", "Generosity"),
    ]
    frames = []
    for spec in candidates:
        path, country_col, score_col, gdp_col, health_col, support_col, freedom_col, corruption_col, generosity_col = spec
        p = raw / path
        if not p.exists():
            continue
        df = pd.read_csv(p)
        required = [country_col, score_col]
        if not all(c in df.columns for c in required):
            continue
        out = pd.DataFrame({
            "country": df[country_col].astype(str),
            "happiness_score": pd.to_numeric(df[score_col], errors="coerce"),
            "happiness_gdp_component": pd.to_numeric(df.get(gdp_col), errors="coerce"),
            "happiness_health_component": pd.to_numeric(df.get(health_col), errors="coerce"),
            "happiness_social_support": pd.to_numeric(df.get(support_col), errors="coerce"),
            "happiness_freedom": pd.to_numeric(df.get(freedom_col), errors="coerce"),
            "happiness_corruption_trust": pd.to_numeric(df.get(corruption_col), errors="coerce"),
            "happiness_generosity": pd.to_numeric(df.get(generosity_col), errors="coerce"),
            "happiness_year": int(re.search(r"20\d{2}", path).group()),
        })
        out["country_key"] = out["country"].map(country_key)
        frames.append(out)
    if not frames:
        return pd.DataFrame(columns=["country_key", "happiness_score", "happiness_gdp_component", "happiness_health_component", "happiness_social_support", "happiness_freedom", "happiness_corruption_trust", "happiness_generosity", "happiness_year"])
    all_h = pd.concat(frames, ignore_index=True)
    # Keep a pre-pandemic country profile averaged over available 2015-2019 reports.
    metrics = [c for c in all_h.columns if c.startswith("happiness_") and c != "happiness_year"]
    averaged = all_h.groupby("country_key", as_index=False)[metrics].mean()
    averaged = averaged.merge(all_h.groupby("country_key", as_index=False)["happiness_year"].max().rename(columns={"happiness_year":"last_happiness_data_year"}), on="country_key", how="left")
    return averaged

def load_population(raw: Path) -> pd.DataFrame:
    p = find_file(raw, ["population_by_country_2020(1).csv", "population_by_country_2020.csv"])
    if p is not None:
        df = pd.read_csv(p)
        name = "Country (or dependency)"
        pop = "Population (2020)"
        if name in df and pop in df:
            out = pd.DataFrame({"country": df[name], "population_2020_reference": pd.to_numeric(df[pop].astype(str).str.replace(",", "", regex=False), errors="coerce")})
            out["country_key"] = out.country.map(country_key)
            return out.drop_duplicates("country_key")
    p = find_file(raw, ["countries_by_population_2019(1).csv", "countries_by_population_2019.csv"])
    if p is not None:
        df = pd.read_csv(p)
        if "name" in df and "pop2019" in df:
            out = pd.DataFrame({"country": df.name, "population_2020_reference": pd.to_numeric(df.pop2019, errors="coerce")})
            out["country_key"] = out.country.map(country_key)
            return out.drop_duplicates("country_key")
    return pd.DataFrame(columns=["country", "population_2020_reference", "country_key"])

def load_owid(raw: Path) -> pd.DataFrame:
    p = find_file(raw, ["owid-covid-data.xlsx", "owid-covid-data.csv"])
    if p is None:
        raise FileNotFoundError("Primary dataset missing: add owid-covid-data.xlsx to data/raw.")
    df = pd.read_excel(p) if p.suffix.lower() == ".xlsx" else pd.read_csv(p, low_memory=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    numeric = ["total_cases", "new_cases", "total_deaths", "new_deaths", "total_cases_per_million", "new_cases_per_million", "total_deaths_per_million", "new_deaths_per_million", "population", "gdp_per_capita", "median_age", "life_expectancy", "hospital_beds_per_thousand", "human_development_index", "stringency_index", "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred", "reproduction_rate"]
    safe_numeric(df, numeric)
    # Keep actual country records only; OWID also includes continents and world aggregates.
    df = df[df["iso_code"].astype(str).str.match(r"^[A-Z]{3}$", na=False)].copy()
    df = df.sort_values(["location", "date"]).drop_duplicates(["location", "date"], keep="last")
    df["country_key"] = df["location"].map(country_key)
    if "new_cases_per_million" not in df:
        df["new_cases_per_million"] = df["new_cases"] / df["population"] * 1_000_000
    if "new_deaths_per_million" not in df:
        df["new_deaths_per_million"] = df["new_deaths"] / df["population"] * 1_000_000
    # Clip negative corrections for log/rolling forecast features, retain raw column too.
    df["new_cases_per_million_clean"] = df["new_cases_per_million"].clip(lower=0)
    df["new_deaths_per_million_clean"] = df["new_deaths_per_million"].clip(lower=0)
    return df

def create_forecast_data(daily: pd.DataFrame, out: Path) -> dict:
    from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline

    df = daily[["location", "country_key", "date", "new_cases_per_million_clean", "population", "gdp_per_capita", "median_age", "life_expectancy", "hospital_beds_per_thousand", "human_development_index", "stringency_index", "reproduction_rate"]].copy()
    df = df.sort_values(["location", "date"])
    grp = df.groupby("location", sort=False)["new_cases_per_million_clean"]
    for lag in [1, 7, 14, 21]:
        df[f"cases_lag_{lag}"] = grp.shift(lag)
    df["cases_roll7"] = grp.transform(lambda s: s.shift(1).rolling(7, min_periods=4).mean())
    df["cases_roll14"] = grp.transform(lambda s: s.shift(1).rolling(14, min_periods=7).mean())
    df["cases_roll28"] = grp.transform(lambda s: s.shift(1).rolling(28, min_periods=14).mean())
    df["target_next_7d_avg_cases_per_million"] = grp.transform(lambda s: s.shift(-1).rolling(7, min_periods=7).mean().shift(-6))
    # target above is shifted one day then averaged across next 7 dates.
    df["day_of_year"] = df.date.dt.dayofyear
    df["month"] = df.date.dt.month
    df["log_population"] = np.log1p(df.population.clip(lower=0))
    features = ["cases_lag_1", "cases_lag_7", "cases_lag_14", "cases_lag_21", "cases_roll7", "cases_roll14", "cases_roll28", "day_of_year", "month", "log_population", "gdp_per_capita", "median_age", "life_expectancy", "hospital_beds_per_thousand", "human_development_index", "stringency_index", "reproduction_rate"]
    model_df = df.dropna(subset=["target_next_7d_avg_cases_per_million", "date"]).copy()
    # Avoid evaluating rows from locations with very sparse historical data.
    model_df = model_df[model_df["cases_roll7"].notna()]
    if model_df.empty:
        raise ValueError("Not enough valid daily history to train forecasting model.")
    cutoff = model_df["date"].max() - pd.Timedelta(days=21)
    train = model_df[model_df.date < cutoff]
    test = model_df[model_df.date >= cutoff]
    # Guard against tiny test windows in unusual input data.
    if len(train) < 100 or len(test) < 20:
        cutoff = model_df["date"].quantile(0.8)
        train, test = model_df[model_df.date < cutoff], model_df[model_df.date >= cutoff]
    # Bound the tree ensemble training cost while retaining broad country/date coverage.
    rf_train = train.sample(n=min(35000, len(train)), random_state=42) if len(train) > 35000 else train
    X_train, y_train = train[features], train["target_next_7d_avg_cases_per_million"]
    X_test, y_test = test[features], test["target_next_7d_avg_cases_per_million"]
    baseline = test["cases_roll7"].clip(lower=0)
    models = {
        "RandomForest": RandomForestRegressor(n_estimators=70, max_depth=14, min_samples_leaf=5, max_features=0.85, random_state=42, n_jobs=4),
        "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=180, learning_rate=0.08, max_leaf_nodes=20, l2_regularization=1.0, random_state=42),
    }
    metrics = []
    predictions = test[["location", "date", "target_next_7d_avg_cases_per_million", "cases_roll7"]].copy().rename(columns={"target_next_7d_avg_cases_per_million":"actual_next_7d_avg_cases_per_million", "cases_roll7":"baseline_prediction"})
    metrics.append({"model":"7-day rolling mean baseline", "MAE":mean_absolute_error(y_test, baseline), "RMSE":mean_squared_error(y_test, baseline)**0.5, "R2":r2_score(y_test, baseline), "train_rows":len(train), "test_rows":len(test), "test_start":str(test.date.min().date()), "test_end":str(test.date.max().date())})
    predictions["prediction_baseline"] = baseline.values
    for name, model in models.items():
        pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", model)])
        if name == "RandomForest":
            pipe.fit(rf_train[features], rf_train["target_next_7d_avg_cases_per_million"])
        else:
            pipe.fit(X_train, y_train)
        pred = np.maximum(0, pipe.predict(X_test))
        metrics.append({"model":name, "MAE":mean_absolute_error(y_test, pred), "RMSE":mean_squared_error(y_test, pred)**0.5, "R2":r2_score(y_test, pred), "train_rows":len(train), "test_rows":len(test), "test_start":str(test.date.min().date()), "test_end":str(test.date.max().date())})
        predictions[f"prediction_{name.lower()}"] = pred
        import joblib
        joblib.dump(pipe, out.parent.parent / "models" / f"{name.lower()}_forecast.joblib")
    metric_df = pd.DataFrame(metrics).sort_values("MAE")
    metric_df.to_csv(out / "forecast_model_metrics.csv", index=False)
    predictions.to_csv(out / "forecast_test_predictions.csv", index=False)
    return {"best_model":str(metric_df.iloc[0]["model"]), "test_start":str(test.date.min().date()), "test_end":str(test.date.max().date()), "train_rows":int(len(train)), "test_rows":int(len(test)), "metrics":metric_df.to_dict(orient="records")}

def make_charts(country_summary: pd.DataFrame, daily: pd.DataFrame, forecasts: pd.DataFrame, out: Path) -> None:
    figdir = out.parent.parent / "reports" / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 5))
    top = country_summary.dropna(subset=["total_cases_per_million_latest"]).nlargest(12, "total_cases_per_million_latest").sort_values("total_cases_per_million_latest")
    if not top.empty:
        plt.barh(top["country"], top["total_cases_per_million_latest"])
        plt.xlabel("Cumulative confirmed cases per million (latest available record)")
        plt.title("Countries with highest recorded case burden per capita")
        plt.tight_layout(); plt.savefig(figdir / "top_countries_cases_per_million.png", dpi=160); plt.close()
    else: plt.close()
    global_daily = daily.groupby("date", as_index=False)[["new_cases", "new_deaths"]].sum(min_count=1)
    plt.figure(figsize=(10, 5))
    plt.plot(global_daily.date, global_daily.new_cases.rolling(7, min_periods=1).mean(), label="7-day mean new cases")
    plt.plot(global_daily.date, global_daily.new_deaths.rolling(7, min_periods=1).mean(), label="7-day mean new deaths")
    plt.title("Global reported COVID-19 trend (7-day rolling mean)"); plt.xlabel("Date"); plt.ylabel("Reported count"); plt.legend(); plt.tight_layout()
    plt.savefig(figdir / "global_daily_trends.png", dpi=160); plt.close()
    if not forecasts.empty:
        chosen = "United States" if "United States" in forecasts["location"].values else forecasts.groupby("location")["actual_next_7d_avg_cases_per_million"].mean().idxmax()
        sub = forecasts[forecasts.location == chosen].sort_values("date").tail(100)
        plt.figure(figsize=(10, 5)); plt.plot(sub.date, sub.actual_next_7d_avg_cases_per_million, label="Actual next-7-day average")
        for col in [c for c in sub if c.startswith("prediction_")]: plt.plot(sub.date, sub[col], label=col.replace("prediction_", "").replace("_", " "), alpha=.8)
        plt.title(f"Forecast test-set comparison: {chosen}"); plt.xlabel("Forecast origin date"); plt.ylabel("Cases per million per day"); plt.legend(); plt.gcf().autofmt_xdate(); plt.tight_layout()
        plt.savefig(figdir / "forecast_actual_vs_predicted.png", dpi=160); plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/raw", help="Folder containing original source files")
    parser.add_argument("--output-dir", default="data/processed", help="Folder for processed outputs")
    args = parser.parse_args()
    raw, out = Path(args.raw_dir), Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (Path("models")).mkdir(exist_ok=True)
    daily = load_owid(raw)
    # Retain report-friendly subset and stable, documented field names.
    keep = [c for c in ["iso_code", "continent", "location", "date", "total_cases", "new_cases", "total_deaths", "new_deaths", "total_cases_per_million", "new_cases_per_million", "total_deaths_per_million", "new_deaths_per_million", "population", "gdp_per_capita", "median_age", "life_expectancy", "hospital_beds_per_thousand", "human_development_index", "stringency_index", "reproduction_rate", "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred", "country_key"] if c in daily]
    daily[keep].to_csv(out / "country_daily_covid.csv", index=False)
    # latest non-null observations by country; use each metric's own last non-null date.
    summary_rows = []
    metric_cols = [c for c in ["total_cases", "total_deaths", "total_cases_per_million", "total_deaths_per_million", "population", "gdp_per_capita", "median_age", "life_expectancy", "hospital_beds_per_thousand", "human_development_index", "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred"] if c in daily]
    for loc, group in daily.groupby("location", sort=False):
        row = {"country":loc, "iso_code":group.iso_code.dropna().iloc[0] if group.iso_code.notna().any() else None, "continent":group.continent.dropna().iloc[0] if group.continent.notna().any() else None, "latest_date":group.date.max(), "country_key":group.country_key.iloc[0]}
        for col in metric_cols:
            vals = group.loc[group[col].notna(), ["date", col]]
            row[col + "_latest"] = vals.iloc[-1][col] if not vals.empty else np.nan
        row["new_cases_7d_avg_latest"] = group.sort_values("date")["new_cases_per_million"].tail(7).mean()
        row["new_deaths_7d_avg_latest"] = group.sort_values("date")["new_deaths_per_million"].tail(7).mean()
        summary_rows.append(row)
    country_summary = pd.DataFrame(summary_rows)
    happy = load_happiness(raw)
    pop = load_population(raw)
    country_summary = country_summary.merge(happy, on="country_key", how="left")
    if not pop.empty:
        country_summary = country_summary.merge(pop[["country_key", "population_2020_reference"]], on="country_key", how="left")
    country_summary["cases_per_100k_latest"] = country_summary["total_cases_per_million_latest"] / 10
    country_summary["deaths_per_100k_latest"] = country_summary["total_deaths_per_million_latest"] / 10
    country_summary.to_csv(out / "country_impact_summary.csv", index=False)
    # Pre-pandemic happiness / economic relationships are descriptive, not causal.
    hcols = [c for c in ["happiness_score", "happiness_gdp_component", "happiness_health_component", "happiness_social_support", "happiness_freedom", "happiness_corruption_trust", "happiness_generosity", "total_cases_per_million_latest", "total_deaths_per_million_latest", "cases_per_100k_latest", "deaths_per_100k_latest", "gdp_per_capita_latest", "human_development_index_latest"] if c in country_summary]
    corr = country_summary[hcols].corr(numeric_only=True) if len(hcols) > 1 else pd.DataFrame()
    corr.to_csv(out / "happiness_economic_covid_correlations.csv")
    # USA county summary from cumulative wide-format JHU-style files.
    us_path = find_file(raw, ["time_series_covid_19_confirmed_US.csv", "time_series_covid_19_confirmed_US(1).csv"])
    death_path = find_file(raw, ["time_series_covid_19_deaths_US.csv", "time_series_covid_19_deaths_US(1).csv"])
    county_summary = pd.DataFrame()
    if us_path:
        us = pd.read_csv(us_path, low_memory=False)
        date_cols = [c for c in us.columns if re.match(r"^\d{1,2}/\d{1,2}/\d{2}$", str(c))]
        base_cols = [c for c in ["UID", "iso3", "FIPS", "Admin2", "Province_State", "Country_Region", "Combined_Key", "Population"] if c in us]
        if date_cols:
            last = date_cols[-1]
            county_summary = us[base_cols].copy()
            county_summary["confirmed_latest"] = pd.to_numeric(us[last], errors="coerce")
            county_summary["latest_date"] = pd.to_datetime(last, format="%m/%d/%y")
            if "Population" in county_summary.columns:
                county_pop = pd.to_numeric(county_summary["Population"], errors="coerce").where(pd.to_numeric(county_summary["Population"], errors="coerce") > 0)
                county_summary["cases_per_100k"] = county_summary["confirmed_latest"] / county_pop * 100000
            else:
                county_summary["cases_per_100k"] = np.nan
            if death_path:
                deaths = pd.read_csv(death_path, low_memory=False)
                dcols = [c for c in deaths.columns if re.match(r"^\d{1,2}/\d{1,2}/\d{2}$", str(c))]
                if dcols:
                    death_keys = [c for c in ["UID", "Combined_Key"] if c in deaths.columns and c in county_summary.columns]
                    if death_keys:
                        dlast = dcols[-1]
                        d = deaths[death_keys].copy()
                        d["deaths_latest"] = pd.to_numeric(deaths[dlast], errors="coerce")
                        if "Population" in deaths.columns:
                            d["Population_from_deaths"] = pd.to_numeric(deaths["Population"], errors="coerce")
                        county_summary = county_summary.merge(d.drop_duplicates(death_keys), on=death_keys, how="left")
                        if "Population" not in county_summary.columns and "Population_from_deaths" in county_summary.columns:
                            county_summary["Population"] = county_summary["Population_from_deaths"]
                        if "Population" in county_summary.columns:
                            county_pop = pd.to_numeric(county_summary["Population"], errors="coerce").where(pd.to_numeric(county_summary["Population"], errors="coerce") > 0)
                            county_summary["cases_per_100k"] = county_summary["confirmed_latest"] / county_pop * 100000
                            county_summary["deaths_per_100k"] = county_summary["deaths_latest"] / county_pop * 100000
            county_summary = county_summary.drop(columns=["Population_from_deaths"], errors="ignore")
            county_summary.to_csv(out / "us_county_impact_summary.csv", index=False)
    forecast_info = create_forecast_data(daily, out)
    forecasts = pd.read_csv(out / "forecast_test_predictions.csv")
    make_charts(country_summary, daily, forecasts, out)
    info = {
        "daily_rows": int(len(daily)), "countries": int(daily.location.nunique()),
        "date_start": str(daily.date.min().date()), "date_end": str(daily.date.max().date()),
        "happiness_countries_matched": int(country_summary.happiness_score.notna().sum()) if "happiness_score" in country_summary else 0,
        "population_reference_matches": int(country_summary.population_2020_reference.notna().sum()) if "population_2020_reference" in country_summary else 0,
        "us_county_rows": int(len(county_summary)), "forecast": forecast_info,
    }
    (out / "run_summary.json").write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")
    print(json.dumps(info, indent=2, default=str))

if __name__ == "__main__":
    main()
