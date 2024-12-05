import subprocess

def setup_and_start_cloudflared():
    try:
        # Add Cloudflare GPG key
        print("Adding Cloudflare GPG key...")
        subprocess.run(
            ["sudo", "mkdir", "-p", "--mode=0755", "/usr/share/keyrings"],
            check=True
        )
        subprocess.run(
            "curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null",
            shell=True,
            check=True
        )
        
        # Add the repository
        print("Adding Cloudflare repository...")
        repo_entry = "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared jammy main"
        subprocess.run(
            f"echo '{repo_entry}' | sudo tee /etc/apt/sources.list.d/cloudflared.list",
            shell=True,
            check=True
        )
        
        # Update and install cloudflared
        print("Installing cloudflared...")
        subprocess.run(
            "sudo apt-get update && sudo apt-get install -y cloudflared",
            shell=True,
            check=True
        )
        
        # Start the cloudflared tunnel on port 5000
        print("Starting cloudflared tunnel on port 5000...")
        subprocess.run(
            ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
            check=True
        )
        print("Cloudflared tunnel started successfully on port 5000!")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return False

    return True

# Run the function
setup_and_start_cloudflared()
