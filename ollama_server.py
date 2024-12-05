import subprocess
from datetime import datetime
import time
from threading import Thread

LOG_FILE = "/content/ollama_serve.log"

def monitor_ollama_serve():
    """
    Monitors the 'ollama serve' command in a separate thread, restarting it if it is killed.
    Logs output to a file.
    """
    command = ["ollama", "serve"]

    while True:
        log_message("Starting 'ollama serve'...")
        try:
            # Create a thread to run the command
            process_thread = Thread(target=_run_process, args=(command,), daemon=True)
            process_thread.start()

            # Wait for the thread to finish
            process_thread.join()

            log_message("'ollama serve' thread finished. Restarting...")
        except Exception as e:
            log_message(f"Error occurred: {e}")
            log_message("Retrying in 5 seconds...")
            time.sleep(5)

def _run_process(command):
    """
    Runs the specified command and logs its output to a file. This function is executed in a thread.

    :param command: The command to execute as a list of arguments.
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Log the output streams
        stdout_thread = _log_stream_to_file(process.stdout, "[stdout]")
        stderr_thread = _log_stream_to_file(process.stderr, "[stderr]")

        # Wait for the process to finish
        process.wait()

        # Stop logging threads
        stdout_thread.join()
        stderr_thread.join()

        log_message(f"'ollama serve' exited with code {process.returncode}")

    except Exception as e:
        log_message(f"Error running process: {e}")

def _log_stream_to_file(stream, prefix):
    """
    Logs lines from a stream to a file with a prefix in a separate thread.

    :param stream: The stream to read lines from.
    :param prefix: The prefix to prepend to each line of output.
    """
    def log_lines():
        try:
            for line in iter(stream.readline, ""):
                if line:
                    log_message(f"{prefix} {line.strip()}")
        except Exception as e:
            log_message(f"Error logging stream: {e}")
        finally:
            stream.close()

    thread = Thread(target=log_lines, daemon=True)
    thread.start()
    return thread

def log_message(message):
    """
    Logs a message to the log file with a timestamp.

    :param message: The message to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# To start monitoring
if __name__ == "__main__":
    monitor_ollama_serve()
