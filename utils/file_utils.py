import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

from utils.database_utils import get_favorite_flows

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

def load_flows_data() -> Dict[str, Any]:
    """Load flows data from database."""
    from utils.database_utils import get_all_flows
    return get_all_flows()

def load_poses_data() -> Dict[str, Any]:
    """Load poses data from database."""
    from utils.database_utils import get_all_poses
    return get_all_poses()

def load_favorite_flows() -> Dict[str, Any]:
    """Load favorites data from database."""
    from utils.database_utils import get_favorite_flows
    return get_favorite_flows()

def load_favorite_poses() ->Dict[str, Any]:
    from utils.database_utils import get_favorite_poses
    return get_favorite_poses()

def load_favorite_sequences() -> Dict[str, Any]:    
    from utils.database_utils import get_favorite_sequences
    return get_favorite_sequences()

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
        from utils.database_utils import get_db_manager, get_pose_by_name
        db = get_db_manager()        
        with db.get_connection() as conn:
            # Remove direct pose favorites
            pose_info = get_pose_by_name(pose_name)
            conn.execute("DELETE FROM favorite_poses WHERE pose_id = ? ", (pose_info("id"),))               
        logger.info(f"Removed pose '{pose_name}' from favorites")
        return True
        
    except Exception as e:
        logger.error(f"Error removing pose from favorites: {e}")
        return False

def remove_sequence_from_favorites(sequence_name: str) -> bool:
    try:
            from utils.database_utils import get_db_manager, get_sequence_by_name
            db = get_db_manager()        
            with db.get_connection() as conn:
                # Remove direct pose favorites
                sequence_info = get_sequence_by_name(sequence_name)
                conn.execute("DELETE FROM favorite_sequences WHERE sequence_id = ? ", (sequence_info("id"),))               
            logger.info(f"Removed sequence '{sequence_name}' from favorites")
            return True
            
    except Exception as e:
        logger.error(f"Error removing sequence from favorites: {e}")
        return False
    
def remove_flow_from_favorites(flow_name: str) -> bool:
    try:
        from utils.database_utils import get_db_manager, get_flow_by_name
        db = get_db_manager()        
        with db.get_connection() as conn:
            # Remove direct flow favorites
            flow_info = get_flow_by_name(flow_name)
            conn.execute("DELETE FROM favorite_flows WHERE flow_id = ? ", (flow_info("id"),))               
        logger.info(f"Removed flow '{flow_name}' from favorites")
        return True

    except Exception as e:
        logger.error(f"Error removing flow from favorites: {e}")
        return False
