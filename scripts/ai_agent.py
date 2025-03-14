from langchain_groq import ChatGroq
import pandas as pd
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from pydantic import BaseModel # Structured State Management

load_dotenv()

llm=ChatGroq(model="llama-3.3-70b-versatile")

class CleaningState(BaseModel):
    """State schema defining input and output for the LangGraph agent."""
    input_text: str
    structured_response: str = ""

class AIAgent:
    def __init__(self):
        self.graph=self.create_graph()
    
    def create_graph():
        """Creates and returns a LangGraph agent graph with state management."""
        graph = StateGraph(CleaningState)

        def agent_logic(state: CleaningState) -> CleaningState:
            """Processes input and returns a structured response."""
            response = llm.invoke(state.input_text)
            return CleaningState(input_text=state.input_text, structured_response=response)


        graph.add_node("cleaning_agent",agent_logic)  
        graph.add_edge("cleaning_agent",END)
        graph.set_entry_point("cleaning_agent")
        return graph.compile()
    
    def process_data(self, df, batch_size=20):
        """Processes data in batches to avoid OpenAI's token limit."""
        cleaned_responses = []

        for i in range(0, len(df), batch_size):
            df_batch=df.iloc[i:i+batch_size]

            prompt = f"""
            You are an AI Data Cleaning Agent. Analyze the dataset:

            {df_batch.to_string()}
            
            Identify missing values, choose the best imputation strategy (mean, mode, median), 
            remove duplicates, and format text correctly.

            Return the cleaned data as structured text.
            """

            state=CleaningState(input_text=prompt, structured_response="")
            response = self.graph.invoke(state)

            if isinstance(response, dict):
                response = CleaningState(**response)
            
            cleaned_responses.append(response.structured_response)
        
        return "\n".join(cleaned_responses)



