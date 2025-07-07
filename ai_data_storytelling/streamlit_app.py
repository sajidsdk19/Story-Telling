import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page config
st.set_page_config(
    page_title="AI Data Storyteller",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stApp {
        background: transparent;
    }
    .stButton>button {
        background-color: #4361ee;
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3f37c9;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

def analyze_data(df):
    """Analyze the data and generate insights using OpenAI"""
    try:
        # Sample data analysis
        summary = df.describe().to_string()
        
        # Generate insights using OpenAI
        prompt = f"""
        Given the following dataset summary, provide key insights and observations:
        {summary}
        
        Please provide:
        1. Key statistics
        2. Interesting patterns
        3. Potential outliers
        4. Business recommendations
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst providing insights about the given dataset."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message['content']
    
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

def generate_story(insights):
    """Generate a narrative story from the insights"""
    try:
        prompt = f"""
        Convert the following data insights into an engaging, easy-to-understand narrative story:
        {insights}
        
        The story should:
        1. Start with an attention-grabbing introduction
        2. Explain the key findings in a narrative format
        3. Provide context and meaning to the numbers
        4. End with actionable recommendations
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional storyteller who makes data insights engaging and easy to understand."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message['content']
    
    except Exception as e:
        return f"Error generating story: {str(e)}"

def main():
    st.title("📊 AI Data Storyteller")
    st.markdown("Upload your dataset and let AI generate meaningful insights and stories from your data.")
    
    # File upload
    uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Show data preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Analyze button
            if st.button("🔍 Analyze Data"):
                with st.spinner("Analyzing your data..."):
                    # Get insights
                    insights = analyze_data(df)
                    
                    # Generate story
                    story = generate_story(insights)
                    
                    # Display results
                    st.subheader("📊 Data Insights")
                    st.markdown(insights)
                    
                    st.subheader("📖 Data Story")
                    st.markdown(story)
                    
                    # Download buttons
                    st.download_button(
                        label="Download Insights",
                        data=insights,
                        file_name="data_insights.txt",
                        mime="text/plain"
                    )
                    
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
