"""
Base frame for all pages
"""
from . import ctk, Any
from .controller import Controller

class BaseFrame(ctk.CTkFrame):
    """Base frame class that all pages inherit from"""
    def __init__(self, parent: Any, controller: Controller):
        super().__init__(parent)
        self.controller = controller 