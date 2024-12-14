import os
import asyncio
import aiofiles
from dotenv import load_dotenv
import google.generativeai as genai
from templates import gen_string, system_message_l, read_gemini_sysmsg, GOOGLE_API_KEY
api_key = str(GOOGLE_API_KEY[0])

def load_api_model():
  api_key = str(GOOGLE_API_KEY[0])
  print(api_key)
  if api_key == None:
      with open("./api_key", 'r') as f:
         api_key = f.readlines[1]
      genai.configure(api_key=api_key)
      print("API Key: "+api_key)
      return api_key
  else:
      api_key = str(GOOGLE_API_KEY[0])
      genai.configure(api_key=api_key)
      print("API Key: "+api_key)
      return api_key
  if api_key == "":
        print("No Google API key set.")
        return None


async def summarize_audio_async(audio_file_name, sys_message):
    api_key = load_api_model()
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    genai_file = await asyncio.to_thread(genai.upload_file, path=f"{audio_file_name}")
    generation_config = genai.GenerationConfig(max_output_tokens=8192, temperature=temperature)
    system_prompt = gen_string(system_message_l)
    prompt = system_prompt
    print("Gemini System Prompt: " + prompt)

    model = genai.GenerativeModel(system_instruction=prompt, model_name='models/gemini-2.0-flash-exp')
    response = await asyncio.to_thread(model.generate_content, [prompt, genai_file], generation_config=generation_config)

    print(response.text)
    return response.text

async def summarize_text_async(text_input, transcription_file):
    api_key = load_api_model()
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    generation_config = genai.GenerationConfig(max_output_tokens=8192, temperature=temperature)
    system_prompt = gen_string(system_message_l)

    async with aiofiles.open(transcription_file, 'r') as f:
        prompt = await f.read()

    model = genai.GenerativeModel(model_name='models/gemini-2.0-flash-exp', generation_config=generation_config, system_instruction=system_prompt)
    response = await asyncio.to_thread(model.generate_content, prompt, generation_config=generation_config)

    print(response.text)
    return response.text

async def transcribe_audio_async(audio_file_name, transcription_file):

    load_dotenv('./env')
    temperature = 0.1
    api_key = load_api_model()
    generation_config = genai.GenerationConfig(max_output_tokens=-1, temperature=temperature)
    transcribe_model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-exp", generation_config=generation_config)
    genai_file = await asyncio.to_thread(genai.upload_file, path=f"{audio_file_name}")

    if not api_key or not genai_file:
        raise ValueError("API key or file is missing for Gemini model.")
    gemini_message_l = read_gemini_sysmsg()
    transcribe_prompt = gen_string(gemini_message_l)
    prompt = transcribe_prompt
    print("Running Gemini Transcription")
    print("Prompt: "+prompt)
    transcription = await asyncio.to_thread(transcribe_model.generate_content, [transcribe_prompt, genai_file],generation_config=generation_config)

    async with aiofiles.open(transcription_file, "w") as f:
        await f.write(transcription.text)

    return transcription.text

def summarize_audio(audio_file_name, sys_message):
    return asyncio.run(summarize_audio_async(audio_file_name, sys_message))

def summarize_text(text_input, transcription_file):
    return asyncio.run(summarize_text_async(text_input, transcription_file))

def transcribe_audio(audio_file_name, transcription_file):
    return asyncio.run(transcribe_audio_async(audio_file_name, transcription_file))

if __name__ == "__main__":
    load_api_model()