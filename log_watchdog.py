import time
import re
import os
LOG_FILE = "/content/cloudflared_url.txt"
def log_message(message):
    """
    Logs a message to the log file with a timestamp.

    :param message: The message to log.
    """
    with open(LOG_FILE, "a") as f:
        f.write(f"{message}\n")


def monitor_log_for_pattern(log_file_path: str, pattern: str):
    if log_file_path is None:
        log_file_path = log_path
    if pattern is None:
        pattern = url_pattern
    """
    Synchronously monitors a log file for matches to a regex pattern.
    Prints the match to stdout once found.

    :param log_file_path: Path to the log file to monitor.
    :param pattern: Regex pattern to search for.
    """
    print(f"Waiting for {log_file_path} to be created...")

    # Wait until the log file exists
    while not os.path.exists(log_file_path):
        time.sleep(1)

    print(f"File {log_file_path} found. Monitoring for matches...")
    last_position = 0  # Track the last read position

    while True:
        try:
            with open(log_file_path, mode="r") as log_file:
                log_file.seek(last_position)  # Move to the last read position
                for line in log_file:
                    match = re.search(pattern, line)
                    if match:
                        print(f"\033[1;33mCloudflared Tunnel URL: {match.group(0)}\033[0m")
                        log_message({match.group(0)})
                        return {match.group(0)}  # Stop monitoring once a match is found
                last_position = log_file.tell()  # Update the last read position
        except FileNotFoundError:
            # In case the file is deleted after being found
            print(f"File {log_file_path} is no longer accessible.")
            break

        time.sleep(1)  # Wait for 1 second before checking again

if __name__ == "__main__":
    log_path = "/content/cloudflared.log"
    url_pattern = r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com"
    monitor_log_for_pattern(log_path, url_pattern)