import os
import asyncio
import aiofiles
import aiogoogle
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

async def async_upload_file(file_path):
    """Asynchronously upload a file using Google's GenAI."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, genai.upload_file, file_path)

async def summarize_audio(audio_file_name, sys_message):
    """Asynchronously summarize an audio file."""
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    
    # Upload file asynchronously
    genai_file = await async_upload_file(audio_file_name)
    
    # Prepare system prompt
    system_prompt = gen_string(system_message_l)
    prompt = system_prompt
    print(f"Gemini System Prompt: {prompt}")
    
    # Create model and generate content
    model = genai.GenerativeModel(
        system_instruction=prompt, 
        model_name='models/gemini-1.5-pro-latest'
    )
    
    # Run generation in executor to avoid blocking
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, 
        lambda: model.generate_content(
            [prompt, genai_file], 
            generation_config=genai.GenerationConfig(
                max_output_tokens=8192,
                temperature=temperature
            )
        )
    )
    
    print(response.text)
    return response

async def summarize_text(text_input, transcription_file):
    """Asynchronously summarize text from a file."""
    load_dotenv('./env')
    temperature = float(os.getenv('TEMPERATURE'))
    
    # Read transcription file asynchronously
    with open(transcription_file, mode='r') as f:
        prompt = f.read()

    # Create model and generate content
    system_prompt = gen_string(system_message_l)
    model = genai.GenerativeModel(
        system_instruction=system_prompt, 
        model_name='models/gemini-1.5-pro-latest'
    )
    
    # Run generation in executor to avoid blocking
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, 
        lambda: model.generate_content(
            prompt, 
            generation_config=genai.GenerationConfig(
                max_output_tokens=8192,
                temperature=temperature
            )
        )
    )
    
    print(response.text)
    return response.text

async def transcribe_audio(audio_file_name, transcription_file):
    """Asynchronously transcribe an audio file."""
    # Upload file asynchronously
    genai_audio_file = await async_upload_file(audio_file_name)
    
    # Create transcription model
    transcribe_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    transcribe_prompt = "Generate a transcript of the speech."
    
    # Run transcription in executor
    loop = asyncio.get_event_loop()
    transcription = await loop.run_in_executor(
        None, 
        lambda: transcribe_model.generate_content([transcribe_prompt, genai_audio_file])
    )
    
    # Write transcription file asynchronously
    async with aiofiles.open(transcription_file, mode='w') as f:
        await f.write(str(transcription.text))
    
    print(transcription.text)
    return transcription.text

# Example of how to call these async functions
async def main():
    await load_api_model()
    
    # Example usage with async calls
    audio_summary = await summarize_audio('example.mp3', 'system_message')
    text_summary = await summarize_text('input_text', 'transcription.txt')
    transcription = await transcribe_audio('audio.mp3', 'output_transcript.txt')

if __name__ == '__main__':
    asyncio.run(main())