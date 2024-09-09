from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from streamlit import cache_resource

# Streamlit app configuration - Must be the first Streamlit command
st.set_page_config(page_title="LLM for Department of Justice", page_icon="🤖")
st.header("AI based CHATBOT for Law & Justice")

# Load environment variables
load_dotenv()

# Configure the Generative AI model
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API key is missing. Please set the GOOGLE_API_KEY in your environment.")
else:
    genai.configure(api_key=api_key)

# Initialize the generative model
try:
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.error(f"Model initialization error: {e}")
    model = None

# Function to extract text from a text file
def extract_text_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

# Directly extract text from the specific text file
file_path = r"ARTICLES OF IC.txt"
context_text = extract_text_from_file(file_path)

# Function to get the response from the Gemini API with the full context
@cache_resource
def get_gemini_response_with_context(question, context):
    try:
        if not model:
            return "Model not initialized."
        combined_input = f"Here is the content from the file:\n{context}\n\nQuestion: {question}"
        response = model.generate_content(combined_input)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit app logic
user_input = st.text_input("Ask your question:", key="input")
submit = st.button("Submit Question")

if submit:
    if user_input.strip():
        with st.spinner("Generating response..."):
            # Query the Gemini API with the full file content as context
            response = get_gemini_response_with_context(user_input, context_text)
                
        st.subheader("The Response:")
        st.write(response)
        
        # Save the question and response in session history
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        st.session_state['history'].append({'question': user_input, 'response': response})
    else:
        st.error("Please enter a valid question.")

# Display history of previous questions and responses
if 'history' in st.session_state:
    st.write("### Previous Q&A:")
    for idx, item in enumerate(st.session_state['history']):
        st.write(f"*Q{idx + 1}:* {item['question']}")
        st.write(f"*A{idx + 1}:* {item['response']}")
