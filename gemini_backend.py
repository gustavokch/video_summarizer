import os
import subprocess
import ollama
from dotenv import load_dotenv
import google.generativeai as genai
from templates import gen_string
from video_summarizer import system_message_l

def load_api_model():
  if len(os.getenv('READ_API_KEY')) < 5:
      load_dotenv('./api_key')
      api_key = str(os.getenv('GOOGLE_API_KEY'))
  else:
      api_key = str(os.getenv('READ_API_KEY'))
  if api_key == "":
        print("No Google API key set.")
        return
  else:
        genai.configure(api_key=api_key)

def summarize_audio(audio_file_name, sys_message):

    genai_file = genai.upload_file(path=f"{audio_file_name}")

    if len(os.getenv("SYSTEM_MESSAGE")) > 100:
        system_prompt = os.getenv("SYSTEM_MESSAGE")
        prompt = str(system_prompt)
    else:
        system_prompt = gen_string(system_message_l)
  
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    response = model.generate_content([prompt, genai_file])
    print(response.text)
    return response.text