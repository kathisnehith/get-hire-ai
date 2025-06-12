import time
import sys
import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

load_dotenv()

#GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") #st.secrets["GEMINI_API_KEY"]
#GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")#st.secrets["GITHUB_API_KEY"]

def gemini_api_validation(API_KEY, model_name, user_prompt):
    client = genai.Client(api_key=API_KEY)

    gemini_response = client.models.generate_content(
        model=model_name, contents=user_prompt
    )
    return gemini_response.text


def openai_api_validation(API_KEY, model_name, user_prompt):
    client= OpenAI(base_url="https://models.github.ai/inference", api_key=API_KEY)
    
    openai_response = client.chat.completions.create(
    model=model_name,
    messages=[
                {"role": "user", "content": user_prompt}
            ]          
    )

    return openai_response.choices[0].message.content

user_prompt = "Hello, this is a test message to validate the API key."

#gemini_api_validation(GEMINI_API_KEY, "gemini-2.0-flash-lite", user_prompt)
#openai_api_validation(GITHUB_API_KEY, "openai/gpt-4o", user_prompt)