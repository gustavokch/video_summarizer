import asyncio
import os
import subprocess
from ollama_server import monitor_ollama_serve
from log_watchdog import monitor_log_for_pattern
from app import app

async def run_app():
    loop = asyncio.get_event_loop()
    # Run app.run in a separate thread as it is a blocking operation
    await loop.run_in_executor(None, app.run, None, True, '0.0.0.0', 5000)

async def main():
    # Run monitor_ollama_serve and app.run concurrently
    ollama_task = asyncio.create_task(monitor_ollama_serve())
    app_task = asyncio.create_task(run_app())
    
    # Wait for app.run to start before running monitor_log_for_pattern
    await asyncio.sleep(5)
    log_task = asyncio.create_task(monitor_log_for_pattern())
    
    # Wait for all tasks to complete
    await asyncio.gather(ollama_task, app_task, log_task)

if __name__ == '__main__':
    asyncio.run(main())