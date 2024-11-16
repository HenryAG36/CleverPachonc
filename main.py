"""
Main entry point for the League Stats application
"""
from src.ui import LeagueStatsApp

def main():
    """Main function to start the application"""
    app = LeagueStatsApp()
    app.mainloop()

if __name__ == "__main__":
    main()
