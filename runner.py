import asyncio
from ollama_server import monitor_ollama_serve
from log_watchdog import monitor_log_for_pattern
from app import app

async def run_app():
    # Use asyncio.to_thread to run blocking app.run in a separate thread
    await asyncio.to_thread(app.run, debug=True, host='0.0.0.0', port=5000)

async def main():
    # Run tasks in parallel
    await asyncio.gather(
        run_app(),
        asyncio.to_thread(monitor_ollama_serve),
        asyncio.to_thread(monitor_log_for_pattern)
    )

if __name__ == '__main__':
    asyncio.run(main())