import streamlit as st
import pandas as pd
import altair as alt
import ast

st.title("How did the median advertised salary for Data Analysts change from Nov 2022 to April 2025?")

data_jobs = pd.read_parquet(
    "https://storage.googleapis.com/data-analyst-wage-trends/clean/data_jobs_cleaned.parquet"
)

# Strips the skillset array into individual skills
def clean_skillset(val):
    if isinstance(val, list):
        return val
    if pd.isna(val) or val == "[]" or val == "":
        return []
    try:
        return ast.literal_eval(val)
    except:
        return [
            s.strip().replace("'", "").replace('"', "")
            for s in str(val).strip("[]").split(",")
            if s.strip()
        ]

skills_df = data_jobs.copy()
skills_df["skillset_cleaned"] = skills_df["skillset"].apply(clean_skillset)

df_exploded = skills_df.explode("skillset_cleaned")
df_exploded = df_exploded.dropna(subset=["salary_yearly", "skillset_cleaned"])
df_exploded = df_exploded[df_exploded["skillset_cleaned"] != ""]

# Find top 10 frequent skills
top_10_frequent = (
    df_exploded["skillset_cleaned"]
    .value_counts()
    .nlargest(10)
    .index.tolist()
)

df_plot = df_exploded[df_exploded["skillset_cleaned"].isin(top_10_frequent)].copy()

# Find top 3 skills by median salary
top_3_salaries = (
    df_plot.groupby("skillset_cleaned")["salary_yearly"]
    .median()
    .nlargest(3)
    .index.tolist()
)

color_condition = alt.condition(
    alt.FieldOneOfPredicate(field="skillset_cleaned", oneOf=top_3_salaries),
    alt.value("#2ca02c"),  # Green
    alt.value("#a9a9a9")   # Gray
)

# Violin plot 
violin_plot = (
    alt.Chart(df_plot)
    .transform_joinaggregate(
        median_salary="median(salary_yearly)",
        groupby=["skillset_cleaned"],
    )
    .transform_density(
        "salary_yearly",
        as_=["salary_yearly", "density"],
        groupby=["skillset_cleaned", "median_salary"],
        bandwidth=8000,
    )
    .mark_area(orient="horizontal", opacity=0.9)
    .encode(
        y=alt.Y(
            "salary_yearly:Q",
            title="Yearly Salary ($)",
            scale=alt.Scale(domain=[20000, 250000], clamp=True),
        ),
        x=alt.X(
            "density:Q",
            stack="center",
            impute=None,
            title=None,
            axis=alt.Axis(labels=False, ticks=False),
        ),
        color=color_condition,
        tooltip=[
            alt.Tooltip("skillset_cleaned:N", title="Skill"),
            alt.Tooltip("median_salary:Q", title="Median Salary", format="$,.0f"),
        ],
        column=alt.Column(
            "skillset_cleaned:N",
            header=alt.Header(
                title="Skillset",
                labelOrient="bottom",
                labelAngle=0,
                labelPadding=20,
                labelFontSize=12,
                labelFontWeight="bold",
                titleFontSize=14,
                titlePadding=10,
            ),
        ),
    )
    .properties(
        width=80,
        height=400,
        title="Technical Skills Command Higher Salaries Than Administrative Skills",
    )
    .configure_facet(spacing=10)
    .configure_view(stroke=None)
)

# Five number summary
five_number_summary = (
    df_plot.groupby("skillset_cleaned")["salary_yearly"]
    .agg(
        Minimum="min",
        Q1=lambda s: s.quantile(0.25),
        Median="median",
        Q3=lambda s: s.quantile(0.75),
        Maximum="max",
    )
    .sort_values(by="Median", ascending=False)
    .reset_index()
    .rename(columns={"skillset_cleaned": "Skill"})
)

st.altair_chart(violin_plot)
st.dataframe(five_number_summary)

st.caption(
    "Design enhancements: Converted to an active title to emphasize the salary premium of technical skills. "
    "Adjusted x-axis labels to display horizontally instead of slanted for improved visibility. "
    "Applied conditional coloring so top three median salary skills appear in solid green while remaining skills appear in neutral gray for clearer visual emphasis."
)