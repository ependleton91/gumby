# App constants and settings
import pathlib

# Paths
APP_DATA_DIR = pathlib.Path("app_data")
ASSETS_DIR = pathlib.Path("assets")
POSES_IMAGE_DIR = ASSETS_DIR / "images" / "poses"

# File names
SEQUENCES_FILE = APP_DATA_DIR / "sequences.json"
FAVORITES_FILE = APP_DATA_DIR / "user_favorites.json"
SETTINGS_FILE = APP_DATA_DIR / "user_settings.json"

# App settings
APP_NAME = "Gumby"
DEFAULT_WINDOW_SIZE = (1200, 800)
