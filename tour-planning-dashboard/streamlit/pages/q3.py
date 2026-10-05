import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

from common import get_cities_fans_merged, render_aggrid
st.title("High Listener Cities Support Stadium Scale Bookings")

df = get_cities_fans_merged()
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

world_topo = data.world_110m.url
countries = alt.topo_feature(world_topo, 'countries')

base_map = alt.Chart(countries).mark_geoshape(
    fill='#e6e6e6',
    stroke='#ffffff',
    strokeWidth=0.5
).project('equirectangular').properties(
    width=900,
    height=500
)


data_bubbles = alt.Chart(df).mark_circle(
    opacity=0.75,
    stroke='white',
    strokeWidth=0.5
).encode(
    longitude='Longitude:Q',
    latitude='Latitude:Q',
    size=alt.Size('Monthly_Listeners:Q',
                  title='Metro Area Listeners',
                  scale=alt.Scale(range=[10, 800])),
    color=alt.Color('Venue_Potential:N',
                    title='Venue Type',
                    # sorted
                    sort=['Stadium', 'Arena', 'Theater', 'Club'],
                    scale=alt.Scale(scheme='tableau10')),
    order=alt.Order('Monthly_Listeners:Q', sort='descending'),
    tooltip=['City_Name', 'Venue_Potential', 'Monthly_Listeners']
)

final_layered_map = (base_map + data_bubbles).properties(
    title={
        "text": "Global Venue Alignment: High Listener Density Justifies Stadium-Scale Touring in Key Hubs "
    }
).configure_view(strokeWidth=0)


st.altair_chart(final_layered_map, use_container_width=True)



st.caption(
    "High-listener cities support stadium-scale bookings, strengthening Spotify’s planning accuracy by targeting markets that can fill the largest venues. "
)

st.subheader("Underlying Raw Data")

raw_table = df[
    [
        "City_Name",
        "Venue_Potential",
        "Monthly_Listeners"
    ]
].copy()

raw_table["Monthly_Listeners"] = raw_table["Monthly_Listeners"].round(1)
raw_table = raw_table.sort_values("City_Name")
raw_table = raw_table.sort_values(
    by=["City_Name", "Monthly_Listeners"],
    ascending=[True, False]
)
render_aggrid(raw_table)