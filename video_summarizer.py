import os
import subprocess
from typing import Tuple, Optional
import yt_dlp
import gc
import torch
from faster_whisper import WhisperModel, BatchedInferencePipeline
from vram_mgmt import clean_vram

class VideoSummarizer:
    """
    A comprehensive class for downloading, transcribing, and summarizing YouTube videos
    """
    def __init__(self, 
                 download_dir="/tmp/video_downloads", 
                 transcription_dir="/tmp/transcriptions", 
                 summary_dir="/tmp/summaries"):
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
        gc.collect()
        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.empty_cache()
        # Create necessary directories
        for directory in [download_dir, transcription_dir, summary_dir]:
            os.makedirs(directory, exist_ok=True)


    def load_model(self):   
      # Ensure CUDA is available
        self.device = "cuda"
        self.model_size = "faster-whisper-large-v3-turbo"
            # Run on GPU with FP16
        self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
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
            
            return audio_file
        except Exception as e:
            raise Exception(f"Failed to download audio: {e}")
    
    def convert_to_wav(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Convert audio to 16kHz WAV format
        
        Args:
            input_file (str): Path to input audio file
            output_file (str, optional): Path to output WAV file
        
        Returns:
            str: Path to converted WAV file
        """
        if not output_file:
            output_file = os.path.splitext(input_file)[0] + '_16khz.wav'
        
        command = [
            'ffmpeg', '-y', '-i', input_file, '-ar', '16000', '-ac', '1', output_file
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
            transcription_file = os.path.join(self.transcription_dir, os.path.basename(audio_file) + '.txt')
            if os.path.isfile(transcription_file):
              gc.collect()
              torch.cuda.empty_cache()
              gc.collect()
              torch.cuda.empty_cache()
              return transcription_file
            else:
              with open(transcription_file, 'w') as f:    
                  for segment in segments:
                      print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))          
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
              return transcription_file
        except Exception as e:
            raise Exception(f"Transcription failed: {e}")
    
    def summarize_text(self, input_text: str, model_name: str = "artifish/llama3.2-uncensored") -> str:
        """
        Summarize text using Ollama
        
        Args:
            input_text (str): Text to summarize
            model_name (str): Ollama model to use for summarization
        
        Returns:
            str: Generated summary
        """
        try:
            from subprocess import Popen, PIPE
            clean_vram()
            gc.collect()
            torch.cuda.empty_cache()
            gc.collect()
            torch.cuda.empty_cache()          
            process = Popen(
                ["ollama", "run", model_name], 
                stdin=PIPE, stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = process.communicate(input=input_text.encode())
            summary = stdout.decode("utf-8").strip()
            
            summary_file = os.path.join(self.summary_dir, 'summary.txt')
            with open(summary_file, "w") as f:
                f.write(summary)
            
            return summary
        except Exception as e:
            raise Exception(f"Summarization failed: {e}")
    
    def process_video(self, video_url: str, model_name: str) -> Tuple[str, str]:
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
            
            # Convert to WAV
            wav_file = self.convert_to_wav(audio_file)
            
            # Transcribe
            transcription_file = self.transcribe_audio(wav_file)
            gc.collect()
            torch.cuda.empty_cache()   
            clean_vram()         
            # Read transcription
            with open(transcription_file, "r") as f:
                transcription_text = f.read()
            
            # Summarize
            summary = self.summarize_text(transcription_text, model_name)
            
            return transcription_file, summary
        
        except Exception as e:
            raise Exception(f"Video processing failed: {e}")
        
# Available Ollama models
AVAILABLE_MODELS = [
    "artifish/llama3.2-uncensored",
    "qwen2.5:7b-instruct-q4_K_M",
    "qwen-summarizer"
]
