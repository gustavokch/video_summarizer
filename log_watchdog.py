import asyncio
import re
import os
import aiofiles
log_path = "/content/cloudflared.log"
url_pattern = r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com"
async def monitor_log_for_pattern(log_file_path: str, pattern: str):
    if log_file_path == None:
        log_file_path = log_path
    if pattern == None:
        pattern = url_pattern
    """
    Asynchronously monitors a log file for matches to a regex pattern.
    Prints the match to stdout once found.

    :param log_file_path: Path to the log file to monitor.
    :param pattern: Regex pattern to search for.
    """
    print(f"Waiting for {log_file_path} to be created...")
    
    # Wait until the log file exists
    while not os.path.exists(log_file_path):
        await asyncio.sleep(1)

    print(f"File {log_file_path} found. Monitoring for matches...")
    last_position = 0  # Track the last read position

    while True:
        try:
            async with aiofiles.open(log_file_path, mode="r") as log_file:
                await log_file.seek(last_position)  # Move to the last read position
                async for line in log_file:
                    match = re.search(pattern, line)
                    if match:
                        print(f"\033[1;33mCloudflared Tunnel URL: {match.group(0)}\033[0m")
                        #print(f"Cloudflared Tunnel URL: {match.group(0)}")
                        return  # Stop monitoring once a match is found
                last_position = await log_file.tell()  # Update the last read position
        except FileNotFoundError:
            # In case the file is deleted after being found
            print(f"File {log_file_path} is no longer accessible.")
            break

        await asyncio.sleep(1)  # Wait for 1 second before checking again
        
if __name__ == "__main__":
    log_path = "/content/cloudflared.log"
    url_pattern = r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com"
    asyncio.run(monitor_log_for_pattern(log_path, url_pattern))