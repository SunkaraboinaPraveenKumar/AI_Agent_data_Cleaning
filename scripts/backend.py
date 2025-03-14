import sys
import os
import pandas as pd
import io
import aiohttp
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from sqlalchemy import create_engine
from pydantic import BaseModel
import requests
import re
from io import StringIO


sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ai_agent import AIAgent
from data_cleaning import DataCleaning

app=FastAPI()

ai_agent=AIAgent()
cleaner=DataCleaning()

@app.post("/clean-data")
async def clean_data(file: UploadFile = File(...)):
    """Receives file from UI, cleans it using rule-based & AI methods, and returns cleaned JSON."""
    try:
        contents = await file.read()
        file_extension = file.filename.split(".")[-1]

        if file_extension == "csv":
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        elif file_extension == "xlsx":
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")

        # print("Before Cleaning:\n", df)

        df_cleaned = cleaner.clean_data(df)
        # print("After Rule-Based Cleaning:\n", df_cleaned)

        df_ai_cleaned = ai_agent.process_data(df_cleaned)
        # print("After AI Cleaning:\n", df_ai_cleaned)

        if isinstance(df_ai_cleaned, str):
            match = re.search(r"```csv\s*(.*?)\s*```", df_ai_cleaned, re.DOTALL)
            if match:
                csv_text = match.group(1)
            else:
                csv_text = df_ai_cleaned  # fallback if no code block found

            # print("Extracted CSV text:\n", csv_text)  # Debug output
            df_ai_cleaned = pd.read_csv(StringIO(csv_text))
        
        return {"cleaned_data": df_ai_cleaned.to_dict(orient="records")}

    except Exception as e:
        print("ERROR:", str(e))  # Log the error
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    

class DBQuery(BaseModel):
    db_url: str
    query: str

@app.post("/clean-db")
async def clean_db(query: DBQuery):
    """Fetches data from a database, cleans it using AI, and returns cleaned JSON."""
    try:
        engine=create_engine(query.db_url)
        df=pd.read_sql(query.query, engine)

        df_cleaned=cleaner.clean_data(df)

        df_ai_cleaned=ai_agent.process_data(df_cleaned)

        if isinstance(df_ai_cleaned, str):
            from io import StringIO
            df_ai_cleaned = pd.read_csv(StringIO(df_ai_cleaned))

        return {"cleaned_data": df_ai_cleaned.to_dict(orient="records")}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from database: {str(e)}")
    

class APIRequest(BaseModel):
    api_url: str

@app.post("/clean-api")
async def clean_api(api_request: APIRequest):
    """Fetches data from an API, cleans it using AI, and returns cleaned JSON."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_request.api_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch data from API.")
                
                data = await response.json()
                df = pd.DataFrame(data)

                # Step 1: Rule-Based Cleaning
                df_cleaned = cleaner.clean_data(df)

                # Step 2: AI-Powered Cleaning
                df_ai_cleaned = ai_agent.process_data(df_cleaned)

                # Convert AI cleaned data to DataFrame if it's a string
                if isinstance(df_ai_cleaned, str):
                    match = re.search(r"```csv\s*(.*?)\s*```", df_ai_cleaned, re.DOTALL)
                    if match:
                        csv_text = match.group(1)
                    else:
                        csv_text = df_ai_cleaned  # fallback if no code block found

                    # Auto-detect delimiter: if there is a comma, use comma; otherwise, fallback to whitespace
                    if ',' in csv_text:
                        df_ai_cleaned = pd.read_csv(StringIO(csv_text))
                    else:
                        df_ai_cleaned = pd.read_csv(StringIO(csv_text), delim_whitespace=True)

                    # print("API data parsed as:", df_ai_cleaned.head())

                return {"cleaned_data": df_ai_cleaned.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing API data: {str(e)}")

# ------------------------ Run Server ------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
