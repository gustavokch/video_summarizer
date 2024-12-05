import asyncio
import os
import subprocess
from ollama_server import monitor_ollama_serve
from log_watchdog import monitor_log_for_pattern

def run_app():
    subprocess.run(
    "python flask-app.py",
    check=True
        )

def main():
    run_app()   
    asyncio.run(monitor_ollama_serve())
    asyncio.run(monitor_log_for_pattern())
if __name__ == '__main__':
    main()