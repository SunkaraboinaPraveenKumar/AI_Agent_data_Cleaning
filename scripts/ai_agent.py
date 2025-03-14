from langchain_groq import ChatGroq
import pandas as pd
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from pydantic import BaseModel # Structured State Management
from langchain.schema import AIMessage

load_dotenv()

llm=ChatGroq(model="llama-3.1-8b-instant")

class CleaningState(BaseModel):
    """State schema defining input and output for the LangGraph agent."""
    input_text: str
    structured_response: str = ""

class AIAgent:
    def __init__(self):
        self.graph=self.create_graph()
    
    def create_graph(self):
        """Creates and returns a LangGraph agent graph with state management."""
        graph = StateGraph(CleaningState)

        def agent_logic(state: CleaningState) -> CleaningState:
            """Processes input and returns a structured response."""
            response = llm.invoke(state.input_text)
            # Ensure structured_response is a string
            if isinstance(response, AIMessage):
                response = response.content  # Extract the text content

            return CleaningState(input_text=state.input_text, structured_response=response)


        graph.add_node("cleaning_agent",agent_logic)  
        graph.add_edge("cleaning_agent",END)
        graph.set_entry_point("cleaning_agent")
        return graph.compile()
    
    

    def process_data(self, df, batch_size=20):
        """Processes data in batches to avoid token limits and returns cleaned data as CSV."""
        cleaned_responses = []

        for i in range(0, len(df), batch_size):
            df_batch = df.iloc[i:i + batch_size]  # Process 20 rows at a time

            prompt = f"""
            You are an AI Data Cleaning Agent. Analyze the following dataset:

            {df_batch.to_string()}

            Identify missing values, choose the best imputation strategy (mean, mode, or median), remove duplicates, and format text correctly.

            **Important:** Return **only the cleaned dataset** as CSV data enclosed within triple backticks and prefixed with "csv" not any python code. For example:

            ```csv
            userId,id,title,body
            1,1,sunt aut facere...,quia et suscipit...
            1,2,qui est esse...,est rerum tempore vitae...
            ```
            """

            state = CleaningState(input_text=prompt, structured_response="")
            response = self.graph.invoke(state)

            if isinstance(response, dict):
                response = CleaningState(**response)

            cleaned_responses.append(response.structured_response)  # Store results

        return "\n".join(cleaned_responses)  # Combine all cleaned results
