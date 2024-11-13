"""
Main entry point for the League Stats application
"""
try:
    from src.ui import LeagueStatsApp
except ImportError as e:
    print(f"Error importing LeagueStatsApp: {e}")
    raise

def main():
    """Main function to start the application"""
    try:
        app = LeagueStatsApp()
        app.mainloop()
    except Exception as e:
        print(f"Error running application: {e}")
        raise

if __name__ == "__main__":
    main()
