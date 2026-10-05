import streamlit as st
import pandas as pd
import altair as alt

st.title("How do cost-of-living adjusted median salaries for Data Analysts vary across U.S. states in 2023?")

merged_monthly_salary = pd.read_parquet('https://storage.googleapis.com/data-analyst-wage-trends/clean/merged_monthly_salaries.parquet')

merged_2023 = merged_monthly_salary[
    merged_monthly_salary['date_time'].dt.year == 2023
].copy()
merged_2023['real_salary_ratio'] = (
    merged_2023['salary_yearly'] / merged_2023['total_cost']
)

real_salary_by_state_2023 = (
    merged_2023
    .groupby('state', as_index=False)['real_salary_ratio']
    .median()
    .sort_values('real_salary_ratio', ascending=False)
)

# Bar chart
bar_chart = (
    alt.Chart(real_salary_by_state_2023)
    .mark_bar()
    .encode(
        y=alt.Y(
            'state:N',
            sort='-x',
            title='State'
        ),
        x=alt.X(
            'real_salary_ratio:Q',
            title='Median Salary ÷ Cost of Living (2023)'
        ),
        color=alt.Color(
            'real_salary_ratio:Q',
            scale=alt.Scale(
                domain=[real_salary_by_state_2023['real_salary_ratio'].min(),
                        1,
                        real_salary_by_state_2023['real_salary_ratio'].max()],
                range=['#C62828', '#FDD835', '#2E7D32'] #Red for lower Salary to cost ratio, Green for higher Salary to cost ratio
            ),
            legend=alt.Legend(title='Salary / COL Ratio') 
        ),
        tooltip=[
            alt.Tooltip('state:N', title='State'),
            alt.Tooltip('real_salary_ratio:Q', title=' Adjusted Salary Ratio', format='.2f')
        ]
    )
    .properties(
        width=750,
        height=400,
        title='Cost-of-Living Adjusted Median Data Analyst Salaries by State (2023)'
    )
)


st.altair_chart(bar_chart)
st.dataframe(real_salary_by_state_2023)