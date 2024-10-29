import pystray
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import uvicorn
import threading
from fastapi import FastAPI
from pathlib import Path
import json
import sys
import webbrowser
from typing import Set, Dict
import logging
import signal

class PolicyAnalyzerTray:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        # Initialize state
        self.server_running = False
        self.port = 8000
        self.watched_paths: Set[Path] = set()
        self.load_config()
        
        # Initialize API
        self.app = FastAPI()
        self.setup_api_routes()
        
        # Create system tray icon
        self.icon = self.create_tray_icon()
        
        # Start the server in a separate thread
        self.start_server()
    
    def load_config(self):
        """Load saved configuration"""
        config_path = Path.home() / '.policy_analyzer_config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.watched_paths = {Path(p) for p in config.get('watched_paths', [])}
                    self.port = config.get('port', 8000)
            except Exception as e:
                logging.error(f"Error loading config: {e}")
    
    def save_config(self):
        """Save current configuration"""
        config_path = Path.home() / '.policy_analyzer_config.json'
        try:
            with open(config_path, 'w') as f:
                json.dump({
                    'watched_paths': [str(p) for p in self.watched_paths],
                    'port': self.port
                }, f)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def setup_api_routes(self):
        """Setup FastAPI routes"""
        @self.app.get("/paths")
        async def get_paths():
            return {"paths": [str(p) for p in self.watched_paths]}
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "running"}
    
    def create_tray_icon(self) -> pystray.Icon:
        """Create the system tray icon and menu"""
        # Create a simple icon (you should replace this with your own icon)
        image = Image.new('RGB', (64, 64), 'blue')
        
        def add_path():
            path = filedialog.askdirectory()
            if path:
                self.watched_paths.add(Path(path))
                self.save_config()
        
        def open_webapp():
            webbrowser.open(f'http://localhost:{self.port}')
        
        menu = pystray.Menu(
            pystray.MenuItem("Add Path", add_path),
            pystray.MenuItem("Open Web App", open_webapp),
            pystray.MenuItem("Exit", self.stop_application)
        )
        
        return pystray.Icon(
            "PolicyAnalyzer",
            image,
            "Policy Analyzer",
            menu
        )
    
    def start_server(self):
        """Start the FastAPI server in a separate thread"""
        def run_server():
            self.server_running = True
            uvicorn.run(
                self.app,
                host="127.0.0.1",
                port=self.port,
                log_level="error"
            )
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def stop_application(self):
        """Clean shutdown of the application"""
        self.server_running = False
        self.save_config()
        self.icon.stop()
        sys.exit(0)
    
    def run(self):
        """Run the system tray application"""
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, lambda x, y: self.stop_application())
        
        # Run the icon
        self.icon.run()

def main():
    logging.basicConfig(level=logging.INFO)
    app = PolicyAnalyzerTray()
    app.run()

if __name__ == "__main__":
    main()