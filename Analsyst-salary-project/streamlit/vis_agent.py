import pandas as pd
import altair as alt
import json
import traceback
import os
from google import genai
from pydantic import BaseModel, Field
from common import get_merged_monthly_salary, get_data_jobs_cleaned

USE_VERTEXAI = os.environ.get("USE_VERTEXAI")

if USE_VERTEXAI in ('true', 'True', 'TRUE'):
    USE_VERTEXAI = True
    PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")
else:
    USE_VERTEXAI = False
    API_KEY = os.environ.get("API_KEY")

print('Info: USE_VERTEXAI =', USE_VERTEXAI)

GEMINI_FLASH_LITE = 'gemini-2.5-flash-lite' 
GEMINI_FLASH = 'gemini-2.5-flash'
USE_MODEL = GEMINI_FLASH_LITE

class Feasibility(BaseModel):
    feasible: bool = Field(description='Is the user request feasible given the available schemas?')
    reason: str = Field(description='A brief, one sentence explanation of the feasibility decision.')
    selected_dataset: str | None = Field(description='The exact key of the dataset to use. None if not feasible.')
 
class Chart(BaseModel):
    code: str | None = Field(description='Python executable code of your final chart. None if not error occurred.')
    desc: str = Field(description='A 1-3 sentence description of the final chart and what it represents.')

class VisAgent:
    def __init__(self):
        
        if USE_VERTEXAI:
            self.client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
            print('Info: Running on VertexAI')
        else:
            self.client = genai.Client(api_key=API_KEY)
            print('Info: Running on Google AI Studio')

        self.datasets = self._init_datasets() 
        self.schemas = self._extract_schemas()

    def _init_datasets(self):
        datasets = {}
        datasets['merged_monthly_salary'] = get_merged_monthly_salary()
        datasets['data_jobs_cleaned'] = get_data_jobs_cleaned()
        return datasets

    def _extract_schemas(self):
        schemas = {}
        for name, df in self.datasets.items():
            schemas[name] = df.dtypes.astype(str).to_dict()
        return schemas

    def _evaluate_and_select(self, user_prompt: str):
        sys_prompt = f"""
        You are a data scientist. Given the user request and available dataset schemas, 
        determine if the request is feasible. If yes, select the most appropriate dataset.
        The available schemas are: {json.dumps(self.schemas)}
        """
        
        response = self.client.models.generate_content(
            model=USE_MODEL,
            contents=[sys_prompt, user_prompt],
            config={
                'temperature': 0.1, 
                'response_mime_type': 'application/json',
                'response_schema': Feasibility, 
            }
        )
        return response.parsed


    def _generate_code(self, user_prompt: str, dataset_name: str, error_context: str = None):
 
        sys_prompt = f"""
        Write Python code to visualize the user's request using Altair.    
        The data is available in a DataFrame named `df`.
        Schema: {self.schemas[dataset_name]}.
        Be sure to include label the axes and include a tooltip. 
        
        Rules:
        1. Only return executable Python code.
        2. Do NOT use plt.show().
        3. Do NOT save the json. 
        4. Your code will be rendered by a downstream process in Streamlit.
        5. Assign the final chart to a variable named final_chart.   
        """
        if error_context:
            sys_prompt += f'\n\nFIX THIS ERROR from previous attempt:\n{error_context}'
            
        response = self.client.models.generate_content(
            model=USE_MODEL,
            contents=[sys_prompt, user_prompt],
            config={
                'temperature': 0.1, 
                'response_mime_type': 'application/json',
                'response_schema': Chart, 
            }
        )
        
        return response.parsed


    def run(self, user_prompt: str, max_retries: int = 2):
 
        eval_result = self._evaluate_and_select(user_prompt)
        
        if not eval_result.feasible:
            return {'status': 'error', 'message': f'Request not feasible: {eval_result.reason}'}
            
        selected_df = eval_result.selected_dataset
        df = self.datasets[selected_df]
        
        error_msg = ''
        
        for attempt in range(max_retries):
            code_result = self._generate_code(user_prompt, selected_df, error_context=error_msg)
            
            code = code_result.code.replace('```python', '').replace('```', '').strip()
            desc = code_result.desc
            
            local_vars = {'df': df.copy(), 'pd': pd, 'alt': alt}
            try:
                # execute the generated code safely, 
                # the chart object will be stored in local_vars
                exec(code, {}, local_vars)
                chart_obj = local_vars.get('final_chart')
                    
                # return the dataset, chart obj, code, and desc   
                return {
                    'status': 'success', 
                    'dataset': selected_df,
                    'chart_obj': chart_obj,
                    'code': code,
                    'desc': desc
                }
                
            except Exception as e:
                # capture traceback to feed back to the LLM for self-correction
                error_msg = traceback.format_exc()
                
        return {'status': 'error', 'message': 'Failed to generate valid code within retry limit.', 'last_error': error_msg}


if __name__ == '__main__':
    user_prompt = 'What did flu activity look like?'
    va = VisAgent()
    chart_result = va.run(user_prompt)
    print('chart_result:', chart_result)