import os
import subprocess
from typing import Tuple, Optional
import yt_dlp
import gc
import torch
import asyncio
from faster_whisper import WhisperModel, BatchedInferencePipeline
import google.generativeai as genai
from vram_mgmt import clean_vram
from templates import generate_modelfile, create_model_from_file, gen_string, system_message_l
from gemini_backend_test import summarize_audio, load_api_model, transcribe_audio, summarize_text, transcribe_audio_async, summarize_audio_async
#from gemini_backend import summarize_audio, load_api_model, transcribe_audio, summarize_text
from dotenv import load_dotenv
from runner import clean_output_folders

class VideoSummarizer:
    """
    A comprehensive class for downloading, transcribing, and summarizing YouTube videos
    """
    def __init__(self, 
                 download_dir="/tmp/video_downloads", 
                 transcription_dir="/tmp/transcriptions", 
                 summary_dir="/tmp/summaries",
                 modelfile_dir="./modelfiles"):
        """
        Initialize directories for downloads, transcriptions, and summaries
        
        Args:
            download_dir (str): Directory to store downloaded audio files
            transcription_dir (str): Directory to store transcription files
            summary_dir (str): Directory to store summary files
        """
        self.download_dir = download_dir
        self.transcription_dir = transcription_dir
        self.summary_dir = summary_dir
        self.modelfile_dir = modelfile_dir
        gc.collect()
        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.empty_cache()
        # Create necessary directories
        for directory in [download_dir, transcription_dir, summary_dir, modelfile_dir]:
            os.makedirs(directory, exist_ok=True)


    def load_model(self):
        load_dotenv('./env')
        test_cpu = int(os.getenv('TEST_CPU'))

        if test_cpu == 0:
            # Ensure CUDA is available
            self.device = "cuda"
            self.model_size = "mobiuslabsgmbh/faster-whisper-large-v3-turbo"
                # Run on GPU with FP16
            self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
            self.batched_model = BatchedInferencePipeline(model=self.model)
        if test_cpu == 1:
            os.environ["OMP_NUM_THREADS"] = "4"
            self.device = "cpu"
            self.model_size = "openai/whisper-small"
                # Run on CPU with INT8
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            self.batched_model = BatchedInferencePipeline(model=self.model)

    def download_audio(self, youtube_url: str) -> str:
        """
        Download audio from a YouTube video
        
        Args:
            youtube_url (str): URL of the YouTube video
        
        Returns:
            str: Path to the downloaded audio file
        
        Raises:
            Exception: If audio download fails
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.download_dir}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'opus',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                audio_file = ydl.prepare_filename(info)
                audio_file = os.path.splitext(audio_file)[0] + '.opus'
                original_language = info.get('original_audio_language', 'Unknown')
                print("ORIGINAL LANGUAGE: "+str(original_language))
            return audio_file
        except Exception as e:
            raise Exception(f"Failed to download audio: {e}")
    
    def convert_to_wav(self, input_file: str, output_file: Optional[str] = None, sample_rate: Optional[int] = 16000, codec: Optional[str] = 'wav') -> str:
        """
        Convert audio to 16kHz WAV format
        
        Args:
            input_file (str): Path to input audio file
            output_file (str, optional): Path to output WAV file
        
        Returns:
            str: Path to converted WAV file
        """
        if not output_file:
            if sample_rate == 16000 and codec == 'wav':
                output_file = os.path.splitext(input_file)[0] + '_16khz.wav'
            if sample_rate == 44100 and codec =='mp3':
                output_file = os.path.splitext(input_file)[0] + '_44khz.mp3'
        
        command = [
            'ffmpeg', '-y', '-i', input_file, '-ar', f"{sample_rate}", '-ac', '1', output_file
        ]
        subprocess.run(command, check=True)
        
        return output_file
    
    def transcribe_audio(self, audio_file: str) -> str:
        """
        Transcribe audio using WhisperX on CUDA
        
        Args:
            audio_file (str): Path to audio file to transcribe
        
        Returns:
            str: Path to transcription file
        """
        try:

            # or run on GPU with INT8
            # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
            # or run on CPU with INT8
            # model = WhisperModel(model_size, device="cpu", compute_type="int8")
            gc.collect()
            torch.cuda.empty_cache()
            clean_vram()
            self.load_model()
            segments, info = self.batched_model.transcribe(audio_file, batch_size=8)

            print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            transcription_file = os.path.join("/tmp/transcriptions", os.path.basename(audio_file) + '.txt')
            gc.collect()
            torch.cuda.empty_cache()
            gc.collect()
            torch.cuda.empty_cache()
            summarize_timestamps = False
            with open(transcription_file, 'w') as f:    
                for segment in segments:
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                    if summarize_timestamps == True:  
                        f.write("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)+ '\n')
                    else:        
                        f.write(segment.text + '\n')
            segments = list(segments)
              # Output file path
              #result = str(segments)
              # Save the transcription to a text file
              #with open(transcription_file, 'w') as f:
              #    f.write(result)
            gc.collect()
            torch.cuda.empty_cache()
            del self.model
            del self.batched_model
            clean_vram()
            return transcription_file
        except Exception as e:
            raise Exception(f"Transcription failed: {e}")
    
    def summarize_text(self, input_text: str, model_name: str = "artifish/llama3.2-uncensored", sys_message: str = "") -> str:
        """
        Summarize text using Ollama
        
        Args:
            input_text (str): Text to summarize
            model_name (str): Ollama model to use for summarization
        
        Returns:
            str: Generated summary
        """
        try:

            # Optional: Clean up GPU memory if applicable
            gc.collect()
            clean_vram()
            sys_message = gen_string(system_message_l)
        
        except Exception as e:
            raise Exception(f"Summarization failed: {e}")

    
    def process_video(self, video_url: str, model_name: str, transcription_model: str) -> Tuple[str, str, str]:
        """
        Comprehensive method to process a video from URL to summary
        
        Args:
            video_url (str): YouTube video URL
            model_name (str): Ollama model for summarization
        
        Returns:
            Tuple[str, str]: Paths to transcription and summary files
        """
        try:
                # Download audio
                audio_file = self.download_audio(video_url)
                print("Transcription model: "+str(transcription_model))
                print("Summarization model: "+str(model_name))    
                api_key = load_api_model()
                wav_file = self.convert_to_wav(audio_file, sample_rate=44100, codec='mp3')
                audio_file_name = os.path.splitext(audio_file)[0] + '_44khz.mp3'                
                if model_name == 'gemini':
                    api_key = load_api_model()
                    sys_message = gen_string(system_message_l)
                    transcription_file = os.path.join("/tmp/transcriptions", os.path.basename(audio_file) + '.txt')
                    print(f"Transcribing audio with model_name={model_name} and transcription_model={transcription_model}" + " Transcription file: "+str(transcription_file))
                    transcription = asyncio.run(transcribe_audio(audio_file_name=audio_file_name, transcription_file=transcription_file))  # Awaiting coroutine
                    print(f"Summarizing audio file={audio_file_name} with model_name={model_name} and transcription_model={transcription_model}")
                    summary = asyncio.run(summarize_audio(sys_message=sys_message, audio_file_name=audio_file_name))  # Awaiting coroutine
                    print("Summary: " + summary)
                    summary_file = os.path.join(self.summary_dir, 'summary.txt')
                    with open(summary_file, "w") as s_f:
                        s_f.write(summary)  # Write resolved string
                    with open(transcription_file, 'w') as t_f: 
                        t_f.write(transcription)  # Write resolved string                 
                return transcription_file, summary           

        except Exception as e:
            raise Exception(f"Video processing failed: {e}")
        
# Available Ollama models
with open("./models.txt", "r") as available_models:
    model_lines = available_models.readlines()
    AVAILABLE_MODELS = [sub.replace('\n', '') for sub in model_lines]
AVAILABLE_BACKENDS = [ 'ollama',
                    'gemini',
                    'vllm']
system_message_l = ["You are an advanced language model specialized in text summarization. Your task is to process transcribed audio and produce extensive and comprehensive summaries. Follow these guidelines:",
"1. **Context Preservation:** Accurately capture the key points, nuances, and tone of the original content. Maintain the original intent and message of the speaker(s).",
"2. **Clarity and Coherence:** Write the summary in a clear, structured, and logical format, ensuring it flows naturally and is easy to understand.",
"3. **Extensiveness:** Provide a detailed summary that includes all significant aspects of the transcript, such as arguments, examples, and conclusions. Aim to create a thorough representation rather than a brief overview.",
"4. **Segmentation:** If the video covers multiple topics, organize the summary into distinct sections or headings reflecting those topics.",
"5. **Focus on Relevance:** Exclude irrelevant information, filler words, and repetitive content unless they contribute meaningfully to the context.",
"6. **Formatting:** Adhere strictly to the markdown format. Use line breaks, title and subtitle headings, bullet points, numbered lists, or subheadings as appropriate to enhance readability and comprehension.",
"7. **Neutrality:** Remain objective and avoid introducing any bias or personal interpretations.",
"Produce a well-rounded and exhaustive summary that provides the reader with a deep understanding of the video content without the need to refer to the original transcript."]

#AVAILABLE_MODELS = [
#    "artifish/llama3.2-uncensored",
#    "qwen2.5:7b-instruct-q4_K_M",
#    "qwen-summarizer"
#]