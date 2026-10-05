import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from st_aggrid import AgGrid, GridOptionsBuilder

def get_merged_monthly_salary():
    merged_monthly_salary = pd.read_parquet('https://storage.googleapis.com/data-analyst-wage-trends/clean/merged_monthly_salaries.parquet')
    return merged_monthly_salary

def get_data_jobs_cleaned():
    df = pd.read_parquet("https://storage.googleapis.com/data-analyst-wage-trends/clean/data_jobs_cleaned.parquet")
    return df


def lookup_dataset_by_name(selected_dataset):
    match selected_dataset:
        case 'merged_monthly_salary':
            return get_merged_monthly_salary()
        case 'data_jobs_cleaned':
            return get_data_jobs_cleaned()
        
def render_aggrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filterable=True, selectable=True, filter="agTextColumnFilter") 
    grid_options = gb.build()
    return AgGrid(df, gridOptions=grid_options, height=400)
