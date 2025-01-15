import json
import tempfile
import csv
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Tuple, List, Optional
import logging
from phi.model.openai import OpenAIChat
from phi.agent.duckdb import DuckDbAgent
from phi.tools.pandas import PandasTools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAnalystApp:
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        
    @staticmethod
    def setup_page_config():
        st.set_page_config(
            page_title="Data Analyst",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    @staticmethod
    def initialize_session_state():
        if "history" not in st.session_state:
            st.session_state.history = []
        if "data_summary" not in st.session_state:
            st.session_state.data_summary = None
            
    @staticmethod
    def handle_uploaded_file(file_uploaded) -> Tuple[Optional[str], Optional[List[str]], Optional[pd.DataFrame]]:
        try:
            # Determine file type and read accordingly
            if file_uploaded.name.endswith('.csv'):
                data = pd.read_csv(file_uploaded, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
            elif file_uploaded.name.endswith('.xlsx'):
                data = pd.read_excel(file_uploaded, na_values=['NA', 'N/A', 'missing'])
            else:
                st.error("Unsupported file type. Please upload a CSV or Excel file.")
                return None, None, None
            
            # Data cleaning and preprocessing
            data = DataAnalystApp.preprocess_data(data)
            
            # Generate and store data summary
            st.session_state.data_summary = DataAnalystApp.generate_data_summary(data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
                temp_file_path = temp_csv.name
                data.to_csv(temp_file_path, index=False, quoting=csv.QUOTE_ALL)
            
            return temp_file_path, list(data.columns), data
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            st.error(f"Error processing the uploaded file: {str(e)}")
            return None, None, None
    
    @staticmethod
    def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
        # Handle string columns
        for col in data.select_dtypes(include=['object']):
            data[col] = data[col].astype(str).replace({r'"': '""'}, regex=True)
        
        # Convert date columns
        date_columns = [col for col in data.columns if 'date' in col.lower()]
        for col in date_columns:
            data[col] = pd.to_datetime(data[col], errors='coerce')
        
        # Handle numeric columns
        numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        return data
    
    @staticmethod
    def generate_data_summary(data: pd.DataFrame) -> dict:
        return {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'missing_values': data.isnull().sum().to_dict(),
            'column_types': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'numeric_summary': data.describe().to_dict() if not data.empty else {},
        }
    
    def create_visualization(self, data: pd.DataFrame, query_result: Optional[pd.DataFrame] = None):
        try:
            df_to_visualize = query_result if query_result is not None else data
            
            st.subheader("📈 Visualization")
            
            # Select columns for visualization
            numeric_cols = df_to_visualize.select_dtypes(include=['float64', 'int64']).columns
            
            if len(numeric_cols) == 0:
                st.warning("No numeric columns available for visualization")
                return
                
            viz_type = st.selectbox(
                "Select visualization type",
                ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("Select X-axis", df_to_visualize.columns)
            
            with col2:
                y_col = st.selectbox("Select Y-axis", numeric_cols)
                
            if viz_type == "Scatter Plot":
                fig = px.scatter(df_to_visualize, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            elif viz_type == "Bar Chart":
                fig = px.bar(df_to_visualize, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            elif viz_type == "Line Chart":
                fig = px.line(df_to_visualize, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
            elif viz_type == "Box Plot":
                fig = px.box(df_to_visualize, x=x_col, y=y_col, title=f"Distribution of {y_col} by {x_col}")
            else:  # Histogram
                fig = px.histogram(df_to_visualize, x=y_col, title=f"Distribution of {y_col}")
            
            st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            logger.error(f"Visualization error: {e}")
            st.warning("Could not generate visualization with the selected options.")
    
    def run(self):
        st.title("📊NIKA - Data Analyst")
        
        # Sidebar configuration
        with st.sidebar:
            self.setup_sidebar()
        
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
        if uploaded_file:
            self.process_uploaded_file(uploaded_file)
    
    def setup_sidebar(self):
        st.header("Configuration")
        openai_api_key = st.text_input("OpenAI API Key:", type="password")
        if openai_api_key:
            st.session_state.api_key = openai_api_key
            st.success("✅ API key saved!")
        
        st.session_state.model = st.selectbox(
            "Select OpenAI Model:",
            ["gpt-4o", "gpt-4o-mini"],
            index=0
        )
        
        if st.session_state.data_summary:
            with st.expander("📊 Data Summary"):
                st.json(st.session_state.data_summary)
    
    def setup_duckdb_agent(self, temp_file: str) -> DuckDbAgent:
        semantic_model_config = {
            "tables": [{
                "name": "user_data",
                "description": "Contains the uploaded dataset.",
                "path": temp_file,
            }]
        }
        
        return DuckDbAgent(
            model=OpenAIChat(
                model=st.session_state.model,
                api_key=st.session_state.api_key
            ),
            semantic_model=json.dumps(semantic_model_config),
            tools=[PandasTools()],
            markdown=True,
            system_prompt="""You are an expert data analyst. Generate SQL queries to answer user questions.
            Provide the SQL query within ```sql ``` tags followed by a clear explanation of the results."""
        )
    
    def process_uploaded_file(self, uploaded_file):
        temp_file, column_list, data_frame = self.handle_uploaded_file(uploaded_file)
        
        if all((temp_file, column_list, data_frame is not None)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("📋 Preview of uploaded data:")
                st.dataframe(data_frame.head(), use_container_width=True)
            
            
            # Setup query interface if API key is provided
            if "api_key" in st.session_state:
                self.setup_query_interface(temp_file, data_frame)
            else:
                st.warning("Please enter your OpenAI API key in the sidebar to enable AI-powered analysis.")
            
            # Show visualization options
            self.create_visualization(data_frame)
    
    def setup_query_interface(self, temp_file: str, data_frame: pd.DataFrame):
        st.subheader("🤖 AI-Powered Analysis")
        duckdb_agent = self.setup_duckdb_agent(temp_file)
        
        # Query input
        query_input = st.text_area(
            "What would you like to know about your data?",
            placeholder="e.g., 'What are the top 5 values in column X?' or 'Show me the average values grouped by Y'"
        )
        
        # Execute query
        if st.button("🚀 Analyze", type="primary"):
            self.process_query(query_input, duckdb_agent, data_frame)
        
        # Display query history
        if st.session_state.history:
            with st.expander("📜 Query History"):
                for i, (q, r) in enumerate(st.session_state.history):
                    st.write(f"Q{i+1}: {q}")
                    st.write(f"A: {r}")
                    st.divider()
    
    def process_query(self, query: str, agent: DuckDbAgent, data_frame: pd.DataFrame):
        if not query.strip():
            st.warning("⚠️ Please enter a query to proceed.")
            return
        
        try:
            with st.spinner('🔄 Processing your query...'):
                response = agent.run(query)
                
                # Store in history
                st.session_state.history.append((query, response.content))
                
                # Display results
                st.markdown("### 📊 Analysis Results")
                st.markdown(response.content)
                
                # Try to extract and visualize results if they're in DataFrame format
                if hasattr(response, 'result') and isinstance(response.result, pd.DataFrame):
                    st.subheader("Query Results Visualization")
                    self.create_visualization(data_frame, response.result)
        
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            st.error(f"❌ Error processing query: {str(e)}")
            st.error("Please try rephrasing your query or check the data format.")

if __name__ == "__main__":
    app = DataAnalystApp()
    app.run()