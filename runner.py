import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Function to start a script without stdout
def run_script_no_stdout(script_name):
    return subprocess.Popen(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Function to start a script with stdout
def run_script_with_stdout(script_name):
    return subprocess.Popen(['python', script_name])

# Watchdog event handler to monitor changes in the cloudflared_url.txt file
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == '/content/cloudflared_url.txt':
            with open('/content/cloudflared_url.txt', 'r') as file:
                print("Cloudflare Tunnel URL: "+str(file.read()))

# Setup and start the watchdog observer
def start_file_watcher():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/content', recursive=False)
    observer.start()
    return observer

def main():
    # Run the scripts in parallel
    p1 = run_script_no_stdout('ollama_server.py')  # No stdout for this script
    p2 = run_script_no_stdout('log_watchdog.py')  # No stdout for this script
    p3 = run_script_with_stdout('app.py')  # With stdout for this script

    # Start the file watcher for cloudflared_url.txt
    observer = start_file_watcher()

    try:
        # Keep the main script running to handle processes and file monitoring
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating scripts...")
        p1.terminate()
        p2.terminate()
        p3.terminate()
        observer.stop()
        observer.join()

if __name__ == '__main__':
    main()
