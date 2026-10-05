import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from st_aggrid import AgGrid, GridOptionsBuilder

def get_cities_fans_merged():
    cities_fans_merged = pd.read_parquet('https://storage.googleapis.com/spotify_data_fans/cities_fans_merged.parquet')
    return cities_fans_merged

def get_city_profiles():
    df = pd.read_parquet("https://storage.googleapis.com/spotify_data_fans/city_profiles.parquet")
    return df


def lookup_dataset_by_name(selected_dataset):
    match selected_dataset:
        case 'cities_fans_merged':
            return get_cities_fans_merged()
        case 'city_profiles':
            return get_city_profiles()
        
def render_aggrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filterable=True, selectable=True, filter="agTextColumnFilter") 
    grid_options = gb.build()
    return AgGrid(df, gridOptions=grid_options, height=400)
