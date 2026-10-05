import streamlit as st
from common import get_city_profiles

q1 = st.Page('pages/q1.py', title='Volume Metrics Mask Critical Audience Friction')
q2 = st.Page('pages/q2.py', title='High Repeat Fan Ratios Reveal Loyal Global Tour Markets')
q3 = st.Page('pages/q3.py', title='High Listener Cities Support Stadium Scale Bookings')
q4 = st.Page('pages/q4.py', title='Lower Skip Rates Signal Stronger Loyalty')

pg = st.navigation([q1, q2, q3, q4])

city_df = get_city_profiles()

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

city_df["Continent"] = city_df["City_Name"].map(city_to_continent)

continent_options = ["All Continents"] + sorted(
    city_df["Continent"].dropna().unique().tolist()
)

st.sidebar.header("Dashboard Filters")

st.session_state["selected_continent"] = st.sidebar.selectbox(
    "Search / filter by continent",
    continent_options,
    index=continent_options.index(
        st.session_state.get("selected_continent", "All Continents")
    )
    if st.session_state.get("selected_continent", "All Continents") in continent_options
    else 0
)

pg.run()