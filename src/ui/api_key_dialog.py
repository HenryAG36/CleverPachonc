"""
API Key Dialog for getting Riot API key from user
"""
import customtkinter as ctk
import webbrowser
from typing import Optional

class APIKeyDialog(ctk.CTkToplevel):
    """Dialog for API key input and validation"""
    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)
        
        # Configure dialog
        self.title("Enter API Key")
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Center dialog on parent
        self.transient(parent)
        self.grab_set()
        
        # Initialize api_key
        self.api_key: Optional[str] = None
        
        # Create main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create title
        title = ctk.CTkLabel(
            main_frame,
            text="Enter your Riot API Key",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=10)
        
        # Create API key entry
        self.key_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            width=300
        )
        self.key_entry.pack(pady=10)
        
        # Create get key button
        get_key_button = ctk.CTkButton(
            main_frame,
            text="Get API Key",
            command=self.open_dev_portal
        )
        get_key_button.pack(pady=10)
        
        # Create submit button
        submit_button = ctk.CTkButton(
            main_frame,
            text="Submit",
            command=self.submit
        )
        submit_button.pack(pady=10)
        
        # Bind enter key to submit
        self.bind("<Return>", lambda e: self.submit())
        
        # Focus entry
        self.key_entry.focus()
    
    def open_dev_portal(self) -> None:
        """Open Riot Developer Portal"""
        webbrowser.open("https://developer.riotgames.com")
    
    def submit(self) -> None:
        """Submit API key"""
        key = self.key_entry.get().strip()
        if key and key.startswith("RGAPI-"):
            self.api_key = key
            self.destroy()