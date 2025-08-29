import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

logger = logging.getLogger(__name__)

# Keep the directory and backup utilities for other files (like images, exports)
def ensure_directory_exists(file_path: Union[str, Path]) -> None:
    """Ensure parent directory exists for given file path."""
    file_path = Path(file_path)
    parent_dir = file_path.parent
    
    try:
        parent_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {parent_dir}")
    except Exception as e:
        logger.error(f"Failed to create directory {parent_dir}: {e}")
        raise

# Replace JSON functions with database functions
def load_flows_data() -> Dict[str, Any]:
    """Load flows data from database."""
    from utils.database_utils import get_all_flows
    return get_all_flows()

def load_poses_data() -> Dict[str, Any]:
    """Load poses data from database."""
    from utils.database_utils import get_all_poses
    return get_all_poses()

def load_favorites_data() -> Dict[str, Any]:
    """Load favorites data from database."""
    from utils.database_utils import get_all_favorites
    return get_all_favorites()

def save_flows_data(data: Dict[str, Any]) -> bool:
    """Save flows data - not needed with database, but kept for compatibility."""
    logger.warning("save_flows_data called - use database_utils.create_flow() instead")
    return True

def save_poses_data(data: Dict[str, Any]) -> bool:
    """Save poses data - not needed with database, but kept for compatibility."""
    logger.warning("save_poses_data called - use database_utils.create_pose() instead")
    return True

def save_favorites_data(data: Dict[str, Any]) -> bool:
    """Save favorites data - not needed with database, but kept for compatibility."""
    logger.warning("save_favorites_data called - use database_utils.create_favorite() instead")
    return True

def update_favorites_after_pose_change(original_name: str, new_name: str, new_pose_data: Dict[str, Any]) -> bool:
    """Update any favorited content that contains the changed pose."""
    try:
        from utils.database_utils import get_db_manager
        import json
        
        db = get_db_manager()
        updated_count = 0
        
        with db.get_connection() as conn:
            # Get favorites that might contain this pose
            cursor = conn.execute("SELECT id, favorite_data FROM favorites WHERE favorite_data LIKE ?", 
                                (f'%"{original_name}"%',))
            favorites = cursor.fetchall()
            
            for favorite in favorites:
                try:
                    favorite_data = json.loads(favorite["favorite_data"]) if favorite["favorite_data"] else {}
                    data_updated = False
                    
                    # Update pose references in flow data
                    if "flow" in favorite_data:
                        for pose in favorite_data["flow"]:
                            if pose.get("name") == original_name:
                                pose["name"] = new_name
                                data_updated = True
                    
                    if data_updated:
                        conn.execute(
                            "UPDATE favorites SET favorite_data = ? WHERE id = ?",
                            (json.dumps(favorite_data), favorite["id"])
                        )
                        updated_count += 1
                
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in favorite {favorite['id']}")
                    continue
            
            # Update favorites that ARE the pose itself
            conn.execute(
                "UPDATE favorites SET name = ? WHERE name = ? AND type = 'pose'",
                (new_name, original_name)
            )
        
        logger.info(f"Updated {updated_count} favorites after pose name change")
        return True
        
    except Exception as e:
        logger.error(f"Error updating favorites after pose change: {e}")
        return False

def remove_pose_from_favorites(pose_name: str) -> bool:
    """Remove a deleted pose from all favorites."""
    try:
        from utils.database_utils import get_db_manager
        import json
        
        db = get_db_manager()
        removed_count = 0
        
        with db.get_connection() as conn:
            # Remove direct pose favorites
            result = conn.execute("DELETE FROM favorites WHERE name = ? AND type = 'pose'", (pose_name,))
            removed_count += result.rowcount
            
            # Update sequences that contain this pose
            cursor = conn.execute("SELECT id, favorite_data FROM favorites WHERE favorite_data LIKE ?", 
                                (f'%"{pose_name}"%',))
            favorites = cursor.fetchall()
            
            for favorite in favorites:
                try:
                    favorite_data = json.loads(favorite["favorite_data"]) if favorite["favorite_data"] else {}
                    
                    if "flow" in favorite_data:
                        original_count = len(favorite_data["flow"])
                        favorite_data["flow"] = [pose for pose in favorite_data["flow"] 
                                               if pose.get("name") != pose_name]
                        
                        if len(favorite_data["flow"]) < original_count:
                            conn.execute(
                                "UPDATE favorites SET favorite_data = ? WHERE id = ?",
                                (json.dumps(favorite_data), favorite["id"])
                            )
                            removed_count += 1
                
                except json.JSONDecodeError:
                    continue
        
        logger.info(f"Removed pose '{pose_name}' from {removed_count} favorites")
        return True
        
    except Exception as e:
        logger.error(f"Error removing pose from favorites: {e}")
        return False

# Export functions for backing up database to JSON
def export_database_to_json(export_dir: Union[str, Path] = "database_export") -> bool:
    """Export entire database to JSON files for backup purposes."""
    try:
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Export poses
        poses_data = load_poses_data()
        with open(export_path / "poses_export.json", 'w') as f:
            import json
            json.dump(poses_data, f, indent=2)
        
        # Export flows
        flows_data = load_flows_data()
        with open(export_path / "flows_export.json", 'w') as f:
            json.dump(flows_data, f, indent=2)
        
        # Export favorites
        favorites_data = load_favorites_data()
        with open(export_path / "favorites_export.json", 'w') as f:
            json.dump(favorites_data, f, indent=2)
        
        logger.info(f"Database exported to {export_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting database: {e}")
        return False