"""
Base frame for all pages
"""
from typing import Any
import customtkinter as ctk

class BaseFrame(ctk.CTkFrame):
    """Base frame class for all pages"""
    def __init__(self, parent: Any, controller: Any):
        super().__init__(parent)
        self.controller = controller 