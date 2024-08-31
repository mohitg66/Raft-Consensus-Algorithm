import os
import platform
import subprocess
import argparse

def open_terminal_and_run(command):
    os_name = platform.system()

    if os_name == "Windows":
        # For Windows
        subprocess.Popen(["cmd", "/k", command])
    elif os_name == "Linux":
        # For Linux (using gnome-terminal)
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"{command}; exec bash"])
    elif os_name == "Darwin":
        # For macOS (using Terminal)
        subprocess.Popen(["open", "-a", "Terminal.app", command])
    else:
        print(f"Unsupported OS: {os_name}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Open a new terminal window and run a command.")
    parser.add_argument("command", type=str, help="The command to execute in the new terminal window.")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Call the function with the provided command
    try:
        open_terminal_and_run(args.command)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
