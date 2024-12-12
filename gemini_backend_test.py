import os
import asyncio
import aiofiles
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
        return None
  else:
        genai.configure(api_key=api_key)

async def summarize_audio_async(audio_file_name, sys_message):
    load_api_model()
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    genai_file = await asyncio.to_thread(genai.upload_file, path=f"{audio_file_name}")
    generation_config = genai.GenerationConfig(max_output_tokens=8192, temperature=temperature)
    system_prompt = gen_string(system_message_l)
    prompt = system_prompt
    print("Gemini System Prompt: " + prompt)

    model = genai.GenerativeModel(system_instruction=prompt, model_name='models/gemini-1.5-pro-latest')
    response = await asyncio.to_thread(model.generate_content, [prompt, genai_file], generation_config=generation_config)

    print(response.text)
    return response.text

async def summarize_text_async(text_input, transcription_file):
    load_api_model()
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    generation_config = genai.GenerationConfig(max_output_tokens=8192, temperature=temperature)
    system_prompt = gen_string(system_message_l)

    async with aiofiles.open(transcription_file, 'r') as f:
        prompt = await f.read()

    model = genai.GenerativeModel(system_instruction=system_prompt, model_name='models/gemini-1.5-pro-latest')
    response = await asyncio.to_thread(model.generate_content, prompt, generation_config=generation_config)

    print(response.text)
    return response.text

async def transcribe_audio_async(audio_file_name, transcription_file):
    load_api_model()
    temperature = float(0.1)
    generation_config = genai.GenerationConfig(max_output_tokens=8192, temperature=temperature)

    transcribe_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    genai_file = await asyncio.to_thread(genai.upload_file, path=f"{audio_file_name}")

    if not api_key or not genai_file:
        raise ValueError("API key or file is missing for Gemini model.")

    transcribe_prompt = "Generate a transcript of the speech."
    print("Running Gemini Transcription")

    transcription = await asyncio.to_thread(transcribe_model.generate_content, [transcribe_prompt, genai_file])

    print(transcription.text)

    async with aiofiles.open(transcription_file, "w") as f:
        await f.write(transcription.text)

    return transcription.text

def summarize_audio(audio_file_name, sys_message):
    return asyncio.run(summarize_audio_async(audio_file_name, sys_message))

def summarize_text(text_input, transcription_file):
    return asyncio.run(summarize_text_async(text_input, transcription_file))

def transcribe_audio(audio_file_name, transcription_file):
    return asyncio.run(transcribe_audio_async(audio_file_name, transcription_file))