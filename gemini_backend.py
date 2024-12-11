import os
import subprocess
import ollama
from dotenv import load_dotenv
import google.generativeai as genai
from templates import gen_string, system_message_l

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
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    genai_file = genai.upload_file(path=f"{audio_file_name}")
    genai.types.GenerationConfig(max_output_tokens=4096,temperature=temperature)
    system_prompt = gen_string(system_message_l)
    prompt = system_prompt
    print("Gemini System Prompt: "+prompt)
    model = genai.GenerativeModel(system_instruction=prompt, model_name='models/gemini-1.5-pro-latest')
    response = model.generate_content([prompt, genai_file], generation_config=genai.GenerationConfig(
        max_output_tokens=8192,
        temperature=temperature
        ))
    print(response.text)
    return response.text

def summarize_text(text_input, transcription_file):
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    genai.types.GenerationConfig(max_output_tokens=8192,temperature=temperature)
    system_prompt = gen_string(system_message_l)
    
    with open(transcription_file) as f:
        prompt = f.read()

    print("Gemini System Prompt: "+prompt)
    model = genai.GenerativeModel(system_instruction=system_prompt, model_name='models/gemini-1.5-pro-latest')
    response = model.generate_content(prompt, generation_config=genai.GenerationConfig(
        max_output_tokens=8192,
        temperature=temperature
        ))
    print(response.text)
    return response.text

def transcribe_audio(audio_file_name, transcription_file):
    transcribe_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    genai_audio_file = genai.upload_file(path=f"{audio_file_name}")
    # Create the prompt.
    transcribe_prompt = "Generate a transcript of the speech."
    # Pass the prompt and the audio file to Gemini.
    transcription = transcribe_model.generate_content([transcribe_prompt, genai_audio_file])
    # Print the transcript.
    print(transcription.text)
    with open(transcription_file, "w") as f:
        f.write(str(transcription.text))
    return transcription.text