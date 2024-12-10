import os
import subprocess
import ollama
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv('./api_key')
api_key = str(os.getenv('GOOGLE_API_KEY'))
system_prompt = os.environ("SYSTEM_MESSAGE")

def load_model():
    if api_key == None:
        print("No Google API key set.")
        return
    else:
        genai.configure(api_key=api_key)

def summarize_text(audio_file_name):
    genai_file = genai.upload_file(path=f{audio_file_name})
    prompt = str(system_prompt)
    model = genai.GenerativeModel('models/gemini-1.5')
    response = model.generate_content([prompt, genai_file])
    print(response.text)
    return response.text