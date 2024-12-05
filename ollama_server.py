import asyncio
from datetime import datetime

LOG_FILE = "ollama_serve.log"

async def monitor_ollama_serve():
    """
    Asynchronously runs the "ollama serve" command and monitors the status of the spawned process,
    restarting it if it is killed. Logs output to a file.
    """
    command = ["ollama", "serve"]  # The command to execute

    while True:
        log_message("Starting 'ollama serve'...")
        try:
            # Start the subprocess
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Monitor the process
            stdout_task = asyncio.create_task(_log_stream_to_file(process.stdout, "[stdout]"))
            stderr_task = asyncio.create_task(_log_stream_to_file(process.stderr, "[stderr]"))

            # Wait for the process to finish
            return_code = await process.wait()

            log_message(f"'ollama serve' exited with code {return_code}")

            # Cancel logging tasks
            stdout_task.cancel()
            stderr_task.cancel()

            # Restart the process if it was killed or crashed
            if return_code != 0:
                log_message("'ollama serve' crashed. Restarting...")
            else:
                log_message("'ollama serve' exited normally. Stopping monitor.")
                break
        except Exception as e:
            log_message(f"Error occurred: {e}")
            log_message("Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def _log_stream_to_file(stream, prefix):
    """
    Asynchronously logs lines from a stream to a file with a prefix.

    :param stream: The stream to read lines from.
    :param prefix: The prefix to prepend to each line of output.
    """
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            log_message(f"{prefix} {line.decode().strip()}")
    except asyncio.CancelledError:
        pass  # Allow cancellation of logging tasks

def log_message(message):
    """
    Logs a message to the log file with a timestamp.

    :param message: The message to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# To start monitoring, run the following in an asyncio loop
if __name__ == "__main__":
    asyncio.run(monitor_ollama_serve())
