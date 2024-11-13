"""
Login window module for API key management
"""
from . import (
    ctk,
    messagebox,
    Any
)
import webbrowser
from ..utils.constants import set_api_key, API_KEY

class APIKeyWindow(ctk.CTkToplevel):
    """Window for API key input and validation"""
    def __init__(self, parent: Any):
        super().__init__(parent)
        
        self.parent = parent
        self.title("Enter API Key")
        self.geometry("400x200")
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, padx=20, pady=20)
        
        # Instructions
        self.instructions = ctk.CTkLabel(
            self.main_frame,
            text="Enter your Riot Games API Key",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.instructions.pack(pady=10)
        
        # API Key entry
        self.api_key_entry = ctk.CTkEntry(
            self.main_frame,
            width=300,
            placeholder_text="RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
        self.api_key_entry.pack(pady=10)
        
        # Paste button
        self.paste_button = ctk.CTkButton(
            self.main_frame,
            text="Paste from Clipboard",
            command=self.paste_from_clipboard
        )
        self.paste_button.pack(pady=5)
        
        # Submit button
        self.submit_button = ctk.CTkButton(
            self.main_frame,
            text="Submit",
            command=self.submit_key
        )
        self.submit_button.pack(pady=5)
        
        # Get key link
        self.get_key_link = ctk.CTkLabel(
            self.main_frame,
            text="Get a key at developer.riotgames.com",
            font=ctk.CTkFont(size=12),
            text_color="blue"
        )
        self.get_key_link.pack(pady=5)
        self.get_key_link.bind("<Button-1>", self.open_riot_dev)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def handle_paste(self, _: Any) -> None:
        """Handle paste event"""
        self.paste_from_clipboard()

    def paste_from_clipboard(self) -> None:
        """Paste API key from clipboard"""
        try:
            clipboard_text = self.clipboard_get()
            self.api_key_entry.delete(0, 'end')
            self.api_key_entry.insert(0, clipboard_text)
        except Exception:
            messagebox.showerror(
                "Error",
                "Could not paste from clipboard"
            )

    def submit_key(self) -> None:
        """Submit API key"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror(
                "Error",
                "Please enter an API key"
            )
            return
            
        if not api_key.startswith("RGAPI-"):
            messagebox.showerror(
                "Error",
                "Invalid API key format.\nAPI keys start with 'RGAPI-'"
            )
            return
        
        # Set the API key
        set_api_key(api_key)
        print(f"API Key length in window: {len(api_key)}")  # Debug print length
        
        # Close window
        self.destroy()

    def open_riot_dev(self, _: Any) -> None:
        """Open Riot Developer Portal"""
        webbrowser.open("https://developer.riotgames.com/")
