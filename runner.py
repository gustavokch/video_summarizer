import asyncio
import os
import subprocess
from ollama_server import monitor_ollama_serve
from log_watchdog import monitor_log_for_pattern

async def ollama_server():
    # Call the monitor function
    await monitor_ollama_serve()
        
async def log_watcher():
    log_path = "/content/cloudflared.log"
    url_pattern = r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com"
    cf_url = await monitor_log_for_pattern(log_path, url_pattern)
    return cf_url

async def run_app():
    subprocess.run(
    "python flask-app.py",
    shell=True,
    check=True
        )

def main():
    asyncio.run(run_app())   
    asyncio.run(ollama_server())
    asyncio.run(log_watcher())
if __name__ == '__main__':
    main()