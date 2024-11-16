"""
UI Module initialization
"""
import customtkinter as ctk
from tkinter import messagebox
import webbrowser
from typing import Any, Dict, List, Optional
from .base_frame import BaseFrame
from .main_window import LeagueStatsApp
from .search_page import SearchPage
from .stats_page import StatsPage
from .api_key_dialog import APIKeyDialog

__all__ = [
    'ctk',
    'messagebox',
    'webbrowser',
    'Any',
    'Dict',
    'List',
    'Optional',
    'BaseFrame',
    'LeagueStatsApp',
    'SearchPage',
    'StatsPage',
    'APIKeyDialog'
]
