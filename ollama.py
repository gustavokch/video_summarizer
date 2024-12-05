import asyncio

async def monitor_ollama_serve():
    """
    Asynchronously runs the "ollama serve" command and monitors the status of the spawned process,
    restarting it if it is killed.
    """
    command = ["ollama", "serve"]  # The command to execute

    while True:
        print("Starting 'ollama serve'...")
        try:
            # Start the subprocess
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Monitor the process
            stdout_task = asyncio.create_task(_log_stream(process.stdout, "[stdout]"))
            stderr_task = asyncio.create_task(_log_stream(process.stderr, "[stderr]"))

            # Wait for the process to finish
            return_code = await process.wait()

            print(f"'ollama serve' exited with code {return_code}")

            # Cancel logging tasks
            stdout_task.cancel()
            stderr_task.cancel()

            # Restart the process if it was killed or crashed
            if return_code != 0:
                print("'ollama serve' crashed. Restarting...")
            else:
                print("'ollama serve' exited normally. Stopping monitor.")
                break
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def _log_stream(stream, prefix):
    """
    Asynchronously logs lines from a stream with a prefix.

    :param stream: The stream to read lines from.
    :param prefix: The prefix to prepend to each line of output.
    """
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            print(f"{prefix} {line.decode().strip()}")
    except asyncio.CancelledError:
        pass  # Allow cancellation of logging tasks

# To start monitoring, run the following in an asyncio loop
if __name__ == "__main__":
    asyncio.run(monitor_ollama_serve())
