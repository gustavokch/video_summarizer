import subprocess
from datetime import datetime
import time

LOG_FILE = "ollama_serve.log"

def monitor_ollama_serve():
    """
    Runs the "ollama serve" command and monitors the status of the spawned process,
    restarting it if it is killed. Logs output to a file.
    """
    command = ["ollama", "serve"]  # The command to execute

    while True:
        log_message("Starting 'ollama serve'...")
        try:
            # Start the subprocess
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
            return_code = process.wait()

            log_message(f"'ollama serve' exited with code {return_code}")

            # Stop logging threads
            stdout_thread.join()
            stderr_thread.join()

            # Restart the process if it was killed or crashed
            if return_code != 0:
                log_message("'ollama serve' crashed. Restarting...")
            else:
                log_message("'ollama serve' exited normally. Stopping monitor.")
                break
        except Exception as e:
            log_message(f"Error occurred: {e}")
            log_message("Retrying in 5 seconds...")
            time.sleep(5)

def _log_stream_to_file(stream, prefix):
    """
    Logs lines from a stream to a file with a prefix.

    :param stream: The stream to read lines from.
    :param prefix: The prefix to prepend to each line of output.
    """
    from threading import Thread

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
