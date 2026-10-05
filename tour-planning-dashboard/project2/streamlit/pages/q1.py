import streamlit as st
import pandas as pd
import altair as alt

from common import get_city_profiles, render_aggrid
st.title("Volume Metrics Mask Critical Audience Friction")

df = get_city_profiles()
city_to_continent = {
    # Africa
    "Johannesburg": "Africa",
    "Lagos": "Africa",

    # Asia
    "Osaka": "Asia",
    "Mumbai": "Asia",
    "Bangkok": "Asia",
    "Tokyo": "Asia",
    "Istanbul": "Asia",
    "Jakarta": "Asia",
    "Manila": "Asia",
    "Seoul": "Asia",

    # Europe
    "Stockholm": "Europe",
    "Paris": "Europe",
    "Milan": "Europe",
    "Madrid": "Europe",
    "Warsaw": "Europe",
    "Amsterdam": "Europe",
    "Berlin": "Europe",
    "London": "Europe",

    # North America
    "Chicago": "North America",
    "Toronto": "North America",
    "New York City": "North America",
    "Los Angeles": "North America",
    "Mexico City": "North America",

    # South America
    "Sao Paulo": "South America",
    "Buenos Aires": "South America",
    "Santiago": "South America",
    "Bogota": "South America",
    "Lima": "South America",

    # Oceania
    "Sydney": "Oceania",
    "Melbourne": "Oceania"
}

df["Continent"] = df["City_Name"].map(city_to_continent)

selected_continent = st.session_state.get("selected_continent", "All Continents")

if selected_continent != "All Continents":
    df = df[df["Continent"] == selected_continent].copy()


scatter = alt.Chart(df).mark_circle(
    size=450,
    opacity=0.9,
    stroke='white',
    strokeWidth=1
).encode(
    x=alt.X('Total_Streams:Q',
        title='Annual Consumption (Total Streams)',
        scale=alt.Scale(domain=[70000000, 260000000], clamp=True),
        axis=alt.Axis(format='~s')),
    y=alt.Y('Save_Rate:Q',
            title='Engagement (Avg. Save Rate %)',
            scale=alt.Scale(zero=False)),
    tooltip=[
        alt.Tooltip('City_Name:N', title='City'),
        alt.Tooltip('Total_Streams:Q', title='Total Streams', format=',d'),
        alt.Tooltip('Save_Rate:Q', title='Save Rate (%)', format='.1f'),
    ]
)

line = scatter.transform_regression(
    'Total_Streams', 'Save_Rate'
).mark_line(color='black', size=3) 

final_matrix = (scatter + line).properties(
    width=850,
    height=550,
    title="Inverse Relationship Between Market Scale and Fan Engagement Exists"
).configure_view(
    strokeWidth=0
)

st.altair_chart(final_matrix, use_container_width=True)
st.caption(
    "As total streams increase, save rates tend to slightly decrease. "
    "Total streams alone are a misleading indicator of where to tour. "
)

st.subheader("Underlying Raw Data")

raw_table = df[
    [
        "City_Name",
        "Total_Streams",
        "Save_Rate"
    ]
].copy()

raw_table["Save_Rate"] = raw_table["Save_Rate"].round(2)
raw_table["Total_Streams"] = raw_table["Total_Streams"].round(2)

render_aggrid(raw_table)
