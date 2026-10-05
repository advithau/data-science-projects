import streamlit as st
import pandas as pd
import altair as alt

st.title("How did the median advertised salary for Data Analysts change from Nov 2022 to April 2025?")

merged_monthly_salary = pd.read_parquet(
    "https://storage.googleapis.com/data-analyst-wage-trends/clean/merged_monthly_salaries.parquet"
)

# Make sure date_time is datetime
merged_monthly_salary["date_time"] = pd.to_datetime(merged_monthly_salary["date_time"])

salary_monthly_national = (
    merged_monthly_salary
    .groupby("date_time", as_index=False)["salary_yearly"]
    .median()
    .sort_values("date_time")
)

salary_monthly_national["rolling_3m"] = (
    salary_monthly_national["salary_yearly"]
    .rolling(window=3, center=True)
    .median()
)

# Year dropdown (2023–2025) + 2022 partial year
year_options = [
    "All (Nov 2022 – Apr 2025)",
    "2022 (Nov–Dec only)",
    "2023",
    "2024",
    "2025",
]

selected_year = st.selectbox("Select a year to display:", year_options, index=0)

# Options for dropdown
if selected_year == "All (Nov 2022 – Apr 2025)":
    plot_df = salary_monthly_national.copy()
elif selected_year == "2022 (Nov–Dec only)":
    plot_df = salary_monthly_national[
        salary_monthly_national["date_time"].dt.year == 2022
    ].copy()
else:
    year_int = int(selected_year)
    plot_df = salary_monthly_national[
        salary_monthly_national["date_time"].dt.year == year_int
    ].copy()

# Line Chart
line_chart = (
    alt.Chart(plot_df)
    .transform_fold(
        ["salary_yearly", "rolling_3m"],
        as_=["Series", "Salary"]
    )
    .transform_calculate(
        SeriesLabel="""
        datum.Series == 'salary_yearly'
        ? 'Monthly Median Salary'
        : 'Rolling Median Salary'
        """
    )
    .mark_line()
    .encode(
        x=alt.X("date_time:T", title="Month"),
y=alt.Y(
    'Salary:Q',
    title='Median Advertised Salary (USD)',
    axis=alt.Axis(format="~s")),
    color=alt.Color(
        "SeriesLabel:N",
            title="",
            legend=alt.Legend(orient="bottom")
        ),
        tooltip=[
            alt.Tooltip("date_time:T", title="Month"),
            alt.Tooltip("salary_yearly:Q", title="Monthly Median Salary", format=",.0f"),
            alt.Tooltip("rolling_3m:Q", title="Rolling Median Salary", format=",.0f"),
        ],
    )
    .properties(
    height=400,
    padding={"left": 60, "right": 10, "top": 10, "bottom": 10}, 
    title=f"Median Advertised Salary for Data Analysts ({selected_year})"
    )
    .interactive()
)

st.altair_chart(line_chart, use_container_width=True)
st.dataframe(plot_df)