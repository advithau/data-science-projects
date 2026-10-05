import streamlit as st
import pandas as pd
import altair as alt

from common import get_city_profiles, render_aggrid
st.title("High Repeat Fan Ratios Reveal Loyal Global Tour Markets")

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


top_5 = df.nlargest(5, 'Repeat_Fan_Ratio')
bottom_5 = df.nsmallest(5, 'Repeat_Fan_Ratio')

extreme_cities = pd.concat([top_5, bottom_5]).drop_duplicates(
    subset=["City_Name"]
).copy()

extreme_cities['Group'] = 'Other'
extreme_cities.loc[
    extreme_cities['City_Name'].isin(top_5['City_Name']),
    'Group'
] = 'Top 5'

color=alt.Color(
    'Group:N',
    scale=alt.Scale(
        domain=['Top 5', 'Other'],
        range=['green', 'lightgray']
    ),
    legend=None
)
contrast_chart = alt.Chart(extreme_cities).mark_bar(
    cornerRadiusEnd=4,
    height=20
).encode(
    x=alt.X(
        'Repeat_Fan_Ratio:Q',
        title='Repeat Fan Ratio (%)',
        scale=alt.Scale(domain=[0, 55]),
        axis=alt.Axis(format='.1f', grid=True, tickCount=6)
    ),
    y=alt.Y(
        'City_Name:N',
        sort='-x',
        title=None
    ),
    color=alt.Color(
        'Group:N',
        scale=alt.Scale(
            domain=['Top 5', 'Other'],
            range=['green', 'lightgray']
        ),
        legend=None
    ),
    tooltip=[
        alt.Tooltip('City_Name:N'),
        alt.Tooltip('Repeat_Fan_Ratio:Q', format='.2f', title='Repeat Ratio %')
    ]
).properties(
    width=600,
    height=400,
    title="Repeat Fan Ratio (% of Returning Monthly Listeners) Reveals Top Tour Markets"
)

st.altair_chart(contrast_chart, use_container_width=True)
st.caption(
    "Cities with higher repeat fan ratios show deeper fan loyalty than markets driven only by one-time listeners. "
    "Prioritizing these cities helps Spotify guide tours toward stronger sellout and revenue opportunities. "
)

st.subheader("Underlying Raw Data")

raw_table = extreme_cities[
    [
        "City_Name",
        "Repeat_Fan_Ratio"
    ]
].copy()

raw_table["Repeat_Fan_Ratio"] = raw_table["Repeat_Fan_Ratio"].round(1)

render_aggrid(raw_table)

