import webview
import threading 
import uvicorn
import asyncio
from backend.server import app
from backend.ollama_manager import ensure_ollama_running, stop_ollama
from backend.database import init_db

# Function that runs the FastAPI server
def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

def on_closed():
    stop_ollama()  # Stop Ollama when the window is closed

def main():
    # Initialize the database
    init_db()

    # Ensure Ollama is running before starting the server
    ollama_ready = asyncio.run(ensure_ollama_running())

    if not ollama_ready:
        print("Warning: Continuing without Ollama running.")

    # Start the FastAPI server in a separate thread | daemon=True means the thread will close when the main program exits
    threading.Thread(target=run_server, daemon=True).start()

    # Creates our window, Titles window 'Rhy', and points it to the FastAPI server
    window = webview.create_window('Rhy', 'http://127.0.0.1:8000')

    # Check if the window was created successfully
    if window is None:
        print("Error: Failed to create the webview window.")
        return
    
    window.events.closed += on_closed  # Attach the on_closed function to the Window's closed event
    webview.start() # Starts the GUI Window

if __name__ == "__main__":
    main()