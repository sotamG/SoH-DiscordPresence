import psutil
import time
import threading
from pypresence.presence import Presence
import pystray
from PIL import Image, ImageDraw
import sys
import os

CLIENT_ID = 1495560691199770817

class SoHDiscordPresence:
    def __init__(self):
        self.rpc = None
        self.is_connected = False
        self.is_running = True
        self.process_running = False
        
    def create_image(self):
        """Load icon from assets folder"""
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        # Fallback to simple icon if file not found
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'darkblue')
        dc = ImageDraw.Draw(image)
        dc.rectangle([width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill='gold')
        return image
    
    def is_soh_running(self):
        """Check if soh.exe is currently running"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == 'soh.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    
    def connect_rpc(self):
        """Connect to Discord RPC"""
        try:
            if not self.rpc:
                self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.is_connected = True
            print("Connected to Discord RPC")
        except Exception as e:
            print(f"Failed to connect to Discord RPC: {e}")
            self.is_connected = False
    
    def update_presence(self):
        """Update Discord Rich Presence"""
        try:
            if self.rpc:
                self.rpc.update(
                    state="Playing Ship of Harkinian",
                    details="The Legend of Zelda: Ocarina of Time",
                    large_image="icon",  # You can set this in Discord Developer Portal
                    large_text="The Legend of Zelda: Ocarina of Time",
                    start=int(time.time())
                )
                print("Discord presence updated")
        except Exception as e:
            print(f"Failed to update presence: {e}")
    
    def disconnect_rpc(self):
        """Disconnect from Discord RPC"""
        try:
            if self.rpc and self.is_connected:
                self.rpc.clear()  # Clear the presence first
                self.rpc.close()
                self.is_connected = False
                print("Disconnected from Discord RPC")
        except Exception as e:
            print(f"Error disconnecting: {e}")
    
    def monitor_process(self):
        """Monitor for soh.exe and manage Discord RPC accordingly"""
        while self.is_running:
            soh_running = self.is_soh_running()
            
            if soh_running and not self.process_running:
                print("soh.exe detected! Connecting to Discord...")
                self.process_running = True
                self.connect_rpc()
                if self.is_connected:
                    self.update_presence()
            
            elif not soh_running and self.process_running:
                print("soh.exe closed. Disconnecting from Discord...")
                self.process_running = False
                self.disconnect_rpc()
            
            time.sleep(5)  # Check every 5 seconds
    
    def on_quit(self, icon, item):
        """Handle quit action from system tray"""
        print("Quitting...")
        self.is_running = False
        self.disconnect_rpc()
        icon.stop()
        sys.exit(0)
    
    def run(self):
        """Start the monitoring thread and system tray icon"""
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
        monitor_thread.start()
        
        # Create system tray icon
        icon = pystray.Icon(
            "SoH Discord Presence",
            self.create_image(),
            "SoH Discord Presence",
            menu=pystray.Menu(
                pystray.MenuItem("Quit", self.on_quit)
            )
        )
        
        print("SoH Discord Presence is running in system tray...")
        icon.run()

if __name__ == "__main__":
    app = SoHDiscordPresence()
    app.run()
