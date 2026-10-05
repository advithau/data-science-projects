import streamlit as st
import pandas as pd
import altair as alt

st.title("Compare Senior and Non-Senior Data Analyst Salaries")

df = pd.read_parquet(
    "https://storage.googleapis.com/data-analyst-wage-trends/clean/data_jobs_cleaned.parquet"
)

df["salary_yearly"] = pd.to_numeric(df["salary_yearly"], errors="coerce")
df = df.dropna(subset=["salary_yearly"])

# Convert index to datetime and pull year from it
df.index = pd.to_datetime(df.index, errors="coerce")
df = df[df.index.notna()].copy()
df["year"] = df.index.year

# Create seniority group once
df["seniority_group"] = df["title"].str.contains(
    r"\bsenior\b", case=False, na=False
).map({True: "Senior", False: "Non-Senior"})

alt.data_transformers.disable_max_rows()

# Dropdown & options
year_options = sorted(df["year"].dropna().unique().tolist())
year_options = ["All Years"] + year_options

selected_year = st.selectbox(
    "Select a year to display:",
    options=year_options,
    index=0
)

if selected_year == "All Years":
    df_plot = df.copy()
else:
    df_plot = df.loc[df["year"] == selected_year].copy()

color_scale = alt.Scale(
    domain=["Non-Senior", "Senior"],
    range=["#E53935", "#1E88E5"]
)

# Boxplot
boxplot = (
    alt.Chart(df_plot)  
    .mark_boxplot(size=55, outliers=True)
    .encode(
        y=alt.Y(
            "seniority_group:N",
            title="Seniority Level",
            sort=["Non-Senior", "Senior"]
        ),
        x=alt.X(
            "salary_yearly:Q",
            title="Advertised Salary (USD)",
            axis=alt.Axis(format="$,.0f")
        ),
        color=alt.Color(
            "seniority_group:N",
            scale=color_scale,
            legend=None
        )
    )
    .properties(
        height=420,
        title=(
            "Senior Data Analysts Command Higher Salaries Than Non-Senior Roles"
            if selected_year == "All Years"
            else f"Senior vs Non-Senior Salaries ({selected_year})"
        )
    )
    .configure_view(stroke=None)
)

st.altair_chart(boxplot, use_container_width=True)

# Five-number summary table
five_number_summary = (
    df_plot.groupby("seniority_group")["salary_yearly"]
      .agg(
          Count="size",
          Minimum="min",
          Q1=lambda x: x.quantile(0.25),
          Median="median",
          Q3=lambda x: x.quantile(0.75),
          Maximum="max"
      )
      .reindex(["Non-Senior", "Senior"])
      .reset_index()
      .rename(columns={"seniority_group": "Seniority Level"})
)

st.dataframe(
    five_number_summary.style.format({
        "Minimum": "${:,.0f}",
        "Q1": "${:,.0f}",
        "Median": "${:,.0f}",
        "Q3": "${:,.0f}",
        "Maximum": "${:,.0f}",
    }),
    use_container_width=True
)

st.caption(
    "Design enhancements: Converted to an active title to emphasize greater senior salaries. "
    "Reoriented the boxplot horizontally to improve readability of salary ranges. "
    "Applied strong contrasting colors to clearly distinguish seniority groups. "
    "All outliers are retained to preserve the full salary distribution without distortion."
)