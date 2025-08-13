import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

# Configure logging for file operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_load_json(file_path: Union[str, Path], default_data: Dict[str, Any]) -> Dict[str, Any]:
    #Load JSON file with comprehensive error handling.
    #Args:
    #    file_path: Path to JSON file
    #    default_data: Data to return if file can't be loaded
        
    #Returns: Dict containing loaded data or default_data
        
    #Example: flows = safe_load_json("app_data/flows.json", {"flowing_sequences": {}})

    file_path = Path(file_path)
    
    try:
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}, using default data")
            return default_data
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded {file_path}")
            return data
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        # Try to create backup of corrupted file
        backup_corrupted_file(file_path)
        return default_data
        
    except PermissionError:
        logger.error(f"Permission denied accessing {file_path}")
        return default_data
        
    except Exception as e:
        logger.error(f"Unexpected error loading {file_path}: {e}")
        return default_data


def safe_save_json(file_path: Union[str, Path], data: Dict[str, Any], create_backup: bool = True) -> bool:
    #Save JSON file with atomic write and optional backup.
    
    #Args:
    #    file_path: Path where to save the file
    #    data: Dictionary to save as JSON
    #    create_backup: Whether to create backup before saving
        
    #Returns:
    #    True if successful, False otherwise
        
    #Example:
    #    success = safe_save_json("app_data/flows.json", flows_data)
    #    if not success:
    #        print("Failed to save file!")
    file_path = Path(file_path)
    
    try:
        # Ensure parent directory exists
        ensure_directory_exists(file_path)
        
        # Create backup if file exists and backup is requested
        if create_backup and file_path.exists():
            backup_success = create_backup_file(file_path)
            if not backup_success:
                logger.warning(f"Failed to create backup for {file_path}")
        
        # Write to temporary file first 
        temp_path = file_path.with_suffix('.tmp')
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Move temp file to final location 
        temp_path.replace(file_path)
        
        logger.info(f"Successfully saved {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save {file_path}: {e}")
        
        # Clean up temp file if it exists
        temp_path = file_path.with_suffix('.tmp')
        if temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
                
        return False


def ensure_directory_exists(file_path: Union[str, Path]) -> None:
    #Ensure parent directory exists for given file path.
    
    #Args:
    #    file_path: File path whose parent directory should exist
        
    #Example:
    #    ensure_directory_exists("app_data/user_settings/preferences.json")
    #    # Creates app_data/user_settings/ if it doesn't exist

    file_path = Path(file_path)
    parent_dir = file_path.parent
    
    try:
        parent_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {parent_dir}")
    except Exception as e:
        logger.error(f"Failed to create directory {parent_dir}: {e}")
        raise


def create_backup_file(file_path: Union[str, Path]) -> bool:
    #Create backup copy of file with timestamp.
    
    #Args:
    #    file_path: Path to file to backup
        
    #Returns:
    #    True if backup created successfully
        
    #Example:
    #    create_backup_file("app_data/flows.json")
    #   Creates app_data/flows.json.backup

    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.warning(f"Cannot backup non-existent file: {file_path}")
        return False
    
    try:
        backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return False


def backup_corrupted_file(file_path: Union[str, Path]) -> bool:
    #Backup a corrupted file for investigation.
    
    #Args:
    #    file_path: Path to corrupted file
        
    #Returns:
    #    True if backup created successfully
  
    file_path = Path(file_path)
    
    try:
        corrupted_path = file_path.with_suffix(f'{file_path.suffix}.corrupted')
        shutil.copy2(file_path, corrupted_path)
        logger.info(f"Backed up corrupted file: {corrupted_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to backup corrupted file {file_path}: {e}")
        return False


def list_backup_files(directory: Union[str, Path]) -> List[Path]:
   # List all backup files in a directory.
    
    #Args:
    #    directory: Directory to search for backups
        
    #Returns:
    #    List of backup file paths
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    backup_files = []
    for file_path in directory.iterdir():
        if file_path.name.endswith('.backup') or file_path.name.endswith('.corrupted'):
            backup_files.append(file_path)
    
    return sorted(backup_files, key=lambda p: p.stat().st_mtime, reverse=True)


def cleanup_old_backups(directory: Union[str, Path], keep_count: int = 5) -> None:
   #Remove old backup files, keeping only the most recent ones.
    
    #Args:
    #    directory: Directory containing backup files
    #    keep_count: Number of recent backups to keep
    
    backup_files = list_backup_files(directory)
    
    if len(backup_files) <= keep_count:
        return
    
    files_to_remove = backup_files[keep_count:]
    
    for file_path in files_to_remove:
        try:
            file_path.unlink()
            logger.info(f"Removed old backup: {file_path}")
        except Exception as e:
            logger.error(f"Failed to remove backup {file_path}: {e}")


# Convenience functions for specific GUMBY files
def load_flows_data() -> Dict[str, Any]:
    """Load flows data with proper defaults."""
    from config import FLOWS_FILE
    return safe_load_json(FLOWS_FILE, {"flowing_sequences": {}})


def load_poses_data() -> Dict[str, Any]:
    """Load poses data with proper defaults."""
    from config import POSES_FILE
    return safe_load_json(POSES_FILE, {"poses": {}})


def load_favorites_data() -> Dict[str, Any]:
    """Load favorites data with proper defaults."""
    from config import FAVORITES_FILE
    return safe_load_json(FAVORITES_FILE, {"favorites": []})


def save_flows_data(data: Dict[str, Any]) -> bool:
    """Save flows data."""
    from config import FLOWS_FILE
    return safe_save_json(FLOWS_FILE, data)


def save_poses_data(data: Dict[str, Any]) -> bool:
    """Save poses data."""
    from config import POSES_FILE
    return safe_save_json(POSES_FILE, data)


def save_favorites_data(data: Dict[str, Any]) -> bool:
    """Save favorites data."""
    from config import FAVORITES_FILE
    return safe_save_json(FAVORITES_FILE, data)