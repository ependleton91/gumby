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
    file_path = Path(file_path)
    
    try:
        ensure_directory_exists(file_path)
        
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
                cleanup_old_backups(temp_path)
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


# Add to the end of utils/file_utils.py

def update_favorites_after_pose_change(original_name: str, new_name: str, new_pose_data: Dict[str, Any]) -> bool:
    """Update any favorited content that contains the changed pose."""
    favorites_data = load_favorites_data()
    favorites_updated = False
    
    for favorite in favorites_data.get("favorites", []):
        # Check if this favorite has flows that contain the updated pose
        if "flow" in favorite:
            for pose in favorite["flow"]:
                if pose.get("name") == original_name:
                    pose["name"] = new_name
                    favorites_updated = True
                    logger.info(f"Updated pose '{original_name}' to '{new_name}' in favorite '{favorite.get('name', 'Unknown')}'")
        
        # If this favorite IS the pose itself
        elif favorite.get("type") == "pose" and favorite.get("name") == original_name:
            favorite["name"] = new_name
            for key, value in new_pose_data.items():
                if key != "image_filename":
                    favorite[key] = value
            favorites_updated = True
            logger.info(f"Updated favorited pose '{original_name}' to '{new_name}'")
    
    if favorites_updated:
        return save_favorites_data(favorites_data)
    return True


def update_favorites_after_flow_change(original_name: str, new_flow_data: Dict[str, Any]) -> bool:
    """Update any favorited content that contains the changed flow."""
    favorites_data = load_favorites_data()
    favorites_updated = False
    
    for favorite in favorites_data.get("favorites", []):
        if favorite.get("name") == original_name and favorite.get("type") == "flow":
            for key, value in new_flow_data.items():
                favorite[key] = value
            favorites_updated = True
            logger.info(f"Updated favorited flow '{original_name}'")
            break
        
        elif "flows" in favorite:
            for i, flow_ref in enumerate(favorite["flows"]):
                if flow_ref.get("name") == original_name:
                    favorite["flows"][i] = new_flow_data.copy()
                    favorites_updated = True
                    logger.info(f"Updated flow '{original_name}' in favorite sequence '{favorite.get('name', 'Unknown')}'")
    
    if favorites_updated:
        return save_favorites_data(favorites_data)
    return True


def remove_pose_from_favorites(pose_name: str) -> bool:
    """Remove a deleted pose from all favorites."""
    favorites_data = load_favorites_data()
    favorites_updated = False
    
    # Remove pose from sequences
    for favorite in favorites_data.get("favorites", []):
        if "flow" in favorite:
            original_count = len(favorite["flow"])
            favorite["flow"] = [pose for pose in favorite["flow"] if pose.get("name") != pose_name]
            if len(favorite["flow"]) < original_count:
                favorites_updated = True
    
    # Remove direct pose favorites
    original_count = len(favorites_data.get("favorites", []))
    favorites_data["favorites"] = [
        fav for fav in favorites_data.get("favorites", [])
        if not (fav.get("type") == "pose" and fav.get("name") == pose_name)
    ]
    if len(favorites_data["favorites"]) < original_count:
        favorites_updated = True
    
    if favorites_updated:
        return save_favorites_data(favorites_data)
    return True


def remove_flow_from_favorites(flow_name: str) -> bool:
    """Remove a deleted flow from all favorites."""
    favorites_data = load_favorites_data()
    favorites_updated = False
    
    # Remove flow from custom sequences
    for favorite in favorites_data.get("favorites", []):
        if "flows" in favorite:
            original_count = len(favorite["flows"])
            favorite["flows"] = [flow for flow in favorite["flows"] if flow.get("name") != flow_name]
            if len(favorite["flows"]) < original_count:
                favorites_updated = True
    
    # Remove direct flow favorites
    original_count = len(favorites_data.get("favorites", []))
    favorites_data["favorites"] = [
        fav for fav in favorites_data.get("favorites", [])
        if not (fav.get("type") == "flow" and fav.get("name") == flow_name)
    ]
    if len(favorites_data["favorites"]) < original_count:
        favorites_updated = True
    
    if favorites_updated:
        return save_favorites_data(favorites_data)
    return True