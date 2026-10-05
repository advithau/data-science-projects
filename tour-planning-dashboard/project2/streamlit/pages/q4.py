import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from common import get_city_profiles, render_aggrid
st.title("Lower Skip Rates Signal Stronger Loyalty")

city_profiles = get_city_profiles()
df = city_profiles.copy()
df['Streams_per_Listener'] = df['Monthly_Streams'] / df['Monthly_Listeners']

df = df[df["Monthly_Listeners"] > 0].copy()
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

min_val = df["Streams_per_Listener"].min()
max_val = df["Streams_per_Listener"].max()

df["Bubble_Size"] = 12 + (
    (df["Streams_per_Listener"] - min_val) / (max_val - min_val)
) * (45 - 12)

fig = px.scatter_mapbox(
    df,
    lat="Latitude",
    lon="Longitude",
    color="Avg_Skip_Rate",           
    hover_name="City_Name",
    hover_data={
        "Avg_Skip_Rate": ":.2f",    
        "Streams_per_Listener": ":.2f",
        "Latitude": False,
        "Longitude": False,
        "Bubble_Size": False         
    },
    zoom=1,
    title="Skip Rates Vary Across Major Global Cities",
    color_continuous_scale="RdYlGn_r"
)

fig.update_traces(
    marker=dict(
        size=df["Bubble_Size"],
        sizemode="diameter",
        opacity=0.8
    )
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin=dict(r=0, t=50, l=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Cities with higher streams per listener + low skip-rate signal stronger listener loyalty/should be prioritized for tour targeting. "
)

st.subheader("Underlying Raw Data")

raw_table = df[
    [
        "City_Name",
        "Avg_Skip_Rate",
        "Streams_per_Listener"
]
].copy()

raw_table["Avg_Skip_Rate"] = raw_table["Avg_Skip_Rate"].round(1)
raw_table["Streams_per_Listener"] = raw_table["Streams_per_Listener"].round(1)

raw_table = raw_table.sort_values(
    by=["Avg_Skip_Rate", "Streams_per_Listener"],
    ascending=[True, False]
)

render_aggrid(raw_table)