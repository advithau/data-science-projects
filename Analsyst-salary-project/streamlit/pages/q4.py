import streamlit as st
import pandas as pd
import altair as alt

st.title("Do remote data analyst positions pay differently than onsite positions, and has this difference evolved?")

data_jobs = pd.read_parquet(
    "https://storage.googleapis.com/data-analyst-wage-trends/clean/data_jobs_cleaned.parquet"
)

alt.data_transformers.disable_max_rows()
work_type = data_jobs.copy()

# create monthly timestamp for grouping
work_type["month"] = work_type.index.to_period("M").to_timestamp()

# monthly median salary by remote status
monthly = (
    work_type.groupby(["month", "work_from_home"], as_index=False)["salary_yearly"]
    .median()
)

monthly["work_mode"] = monthly["work_from_home"].map({True: "Remote", False: "Onsite"})

remote = (
    monthly[monthly["work_from_home"] == True][["month", "salary_yearly"]]
    .rename(columns={"salary_yearly": "remote_median"})
)

onsite = (
    monthly[monthly["work_from_home"] == False][["month", "salary_yearly"]]
    .rename(columns={"salary_yearly": "onsite_median"})
)

gap = remote.merge(onsite, on="month", how="inner")
gap["gap"] = gap["remote_median"] - gap["onsite_median"]
gap["gap_pos"] = gap["gap"].where(gap["gap"] >= 0)
gap["gap_neg"] = gap["gap"].where(gap["gap"] < 0)

all_months = pd.date_range(gap["month"].min(), gap["month"].max(), freq="MS")
gap = (
    gap.set_index("month")
    .reindex(all_months)
    .rename_axis("month")
    .reset_index()
)

pos_line = (
    alt.Chart(gap)
    .mark_line(color="#2E7D32", strokeWidth=3)
    .encode(
        x=alt.X("month:T", title="Month"), # Green to show higher remote salary
        y=alt.Y("gap_pos:Q", title="Remote − Onsite Median Salary (USD)"),
    )
)

neg_line = (
    alt.Chart(gap)
    .mark_line(color="#C62828", strokeWidth=3) # Red to show higher onsite salary
    .encode(
        x=alt.X("month:T", title="Month"),
        y=alt.Y("gap_neg:Q", title="Remote − Onsite Median Salary (USD)"),
    )
)

zero_line = (
    alt.Chart(pd.DataFrame({"y": [0]}))
    .mark_rule(strokeDash=[5, 5])
    .encode(y="y:Q")
)

chart = (pos_line + neg_line + zero_line).properties(
    height=400,
    title="Remote − Onsite Salary Gap Over Time",
).interactive()

legend_df = pd.DataFrame(
    {
        "label": ["Remote Higher", "Onsite Higher"],
        "color": ["#2E7D32", "#C62828"],
        "x": [0, 0],
        "x2": [20, 20],
    }
)

legend = (
    alt.Chart(legend_df)
    .mark_rule(strokeWidth=6)
    .encode(
        y=alt.Y("label:N", title=None),
        x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[0, 30])),
        x2="x2:Q",
        color=alt.Color("color:N", scale=None, legend=None),
    )
    .properties(width=200, height=60)
)

chart_with_legend = (
    alt.vconcat(chart, legend)
    .resolve_scale(color="independent")
    .configure_view(stroke=None)
)

st.altair_chart(chart_with_legend, use_container_width=True)
st.dataframe(gap)

st.caption(
    "Design enhancements: Replaced the area chart with a clean line chart to reduce visual clutter and improve clarity. "
    "Applied conditional coloring so positive values (Remote higher) appear in solid green and negative values (Onsite higher) appear in solid red. "
    "Added a dashed zero reference line to clearly separate gain vs. loss periods. "
    "Moved the legend below the chart and formatted it as compact color swatches to improve readability without distracting from the data."
)