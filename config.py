# App constants and settings
import pathlib

# Paths
APP_DATA_DIR = pathlib.Path("app_data")
ASSETS_DIR = pathlib.Path("assets")
POSES_IMAGE_DIR = ASSETS_DIR / "images" / "poses"

# Database file
DATABASE_FILE = APP_DATA_DIR / "gumby.db"

# Export/backup directories
EXPORT_DIR = APP_DATA_DIR / "exports"
BACKUP_DIR = APP_DATA_DIR / "backups"

# App settings
APP_NAME = "Gumby"
DEFAULT_WINDOW_SIZE = (1200, 800)

# Image settings
POSE_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff']
DEFAULT_POSE_IMAGE = "placeholder.png"
MAX_IMAGE_CACHE_SIZE = 100

# Database settings
DATABASE_BACKUP_KEEP_COUNT = 5
AUTO_BACKUP_ON_STARTUP = True

# Validation constants
MIN_POSE_DURATION = 0.1  # minutes
MAX_POSE_DURATION = 15.0  # minutes
MIN_CLASS_DURATION = 5    # minutes
MAX_CLASS_DURATION = 180  # minutes (3 hours)

# UI constants
POSE_CARD_WIDTH = 300
POSE_CARD_HEIGHT = 200
FLOW_CARD_WIDTH = 400
FLOW_CARD_HEIGHT = 250