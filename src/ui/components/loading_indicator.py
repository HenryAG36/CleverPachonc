import customtkinter as ctk
from typing import Optional

class LoadingIndicator(ctk.CTkFrame):
    def __init__(
        self,
        parent: any,
        text: str = "Loading...",
        width: int = 200,
        height: int = 100
    ):
        super().__init__(parent, width=width, height=height)
        
        # Center the frame
        self.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create loading text
        self.loading_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=16)
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Progress dots animation
        self.dots = ""
        self.dot_count = 0
        self.max_dots = 3
        self.after(500, self.animate_dots)
    
    def animate_dots(self) -> None:
        """Animate the loading dots"""
        self.dot_count = (self.dot_count + 1) % (self.max_dots + 1)
        self.dots = "." * self.dot_count
        self.loading_label.configure(text=f"Loading{self.dots}")
        self.after(500, self.animate_dots)
    
    def update_text(self, text: str) -> None:
        """Update the loading text"""
        self.loading_label.configure(text=text)