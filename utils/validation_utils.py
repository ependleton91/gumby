import re
import logging
from typing import List, Dict, Any, Tuple
from utils.file_utils import load_flows_data, load_poses_data, load_favorites_data
from datetime import datetime

logger = logging.getLogger(__name__)

# All validation functions remain the same - they don't need database changes
def validate_pose_name(name: str) -> Tuple[bool, str]:
    """Validate pose name format and content."""
    if not name or not name.strip():
        return False, "Pose name cannot be empty"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Pose name must be at least 2 characters long"
    
    if len(name) > 100:
        return False, "Pose name is too long (maximum 100 characters)"
    
    # Check for invalid characters (allow letters, numbers, spaces, apostrophes, hyphens)
    if not re.match(r"^[A-Za-z0-9\s\-\']+$", name):
        return False, "Pose name contains invalid characters. Only letters, numbers, spaces, hyphens, and apostrophes are allowed"
    
    # Check for reasonable format (not all numbers or all spaces)
    if name.isdigit():
        return False, "Pose name cannot be only numbers"
    
    if not re.search(r'[A-Za-z]', name):
        return False, "Pose name must contain at least one letter"
    
    if name == "Name Your Pose":
        return False, "Pose name cannot be the default placeholder 'Name Your Pose'"
    
    return True, ""

def validate_duration(duration_str: str, min_duration: float = 0.1, max_duration: float = 600.0) -> Tuple[bool, str, float]:
    """Validate duration input and convert to float."""
    if not duration_str or not duration_str.strip():
        return False, "Duration cannot be empty", 0.0
    
    try:
        duration = float(duration_str.strip())
        
        if duration <= 0:
            return False, "Duration must be greater than 0", 0.0
        
        if duration < min_duration:
            return False, f"Duration must be at least {min_duration} minutes", 0.0
        
        if duration > max_duration:
            return False, f"Duration cannot exceed {max_duration} minutes (10 hours)", 0.0
        
        return True, "", duration
        
    except ValueError:
        return False, "Duration must be a valid number (e.g., 5.5)", 0.0

def validate_difficulty(difficulty_str: str, min_level: int = 1, max_level: int = 5) -> Tuple[bool, str, int]:
    """Validate difficulty level input."""
    if not difficulty_str or not difficulty_str.strip():
        return False, "Difficulty level cannot be empty", min_level
    
    try:
        difficulty = int(difficulty_str.strip())
        
        if difficulty < min_level or difficulty > max_level:
            return False, f"Difficulty must be between {min_level} and {max_level}", min_level
        
        return True, "", difficulty
        
    except ValueError:
        return False, f"Difficulty must be a whole number between {min_level} and {max_level}", min_level

def validate_muscle_groups(muscle_list: List[str]) -> Tuple[bool, str]:
    """Validate muscle group selections."""
    # Define valid muscle groups for yoga poses
    valid_muscles = {
        "core", "abs", "arms", "shoulders", "back", "legs", "thighs", "calves",
        "hips", "glutes", "hamstrings", "quadriceps", "pelvic_floor", 
        "full_body", "neck", "spine", "ankles", "wrists", "chest",
        "side_body", "groin", "hip_flexors", "obliques", "inner_thighs", "balance"
    }
    
    if not muscle_list:
        return False, "At least one muscle group must be selected"
    
    # Check for empty or invalid entries
    cleaned_muscles = []
    for muscle in muscle_list:
        if isinstance(muscle, str) and muscle.strip():
            cleaned_muscles.append(muscle.strip().lower())
    
    if not cleaned_muscles:
        return False, "At least one valid muscle group must be selected"
    
    # Check for invalid muscle groups
    invalid_muscles = [m for m in cleaned_muscles if m not in valid_muscles]
    if invalid_muscles:
        return False, f"Invalid muscle groups: {', '.join(invalid_muscles)}. Valid options include: {', '.join(sorted(valid_muscles))}"
    
    return True, ""

def validate_sequence_name(name: str) -> Tuple[bool, str]:
    """Validate yoga sequence name."""
    if not name or not name.strip():
        return False, "Sequence name cannot be empty"
    
    name = name.strip()
    
    if len(name) < 3:
        return False, "Sequence name must be at least 3 characters long"
    
    if len(name) > 200:
        return False, "Sequence name is too long (maximum 200 characters)"
    
    # Check for reasonable characters
    if not re.match(r"^[A-Za-z0-9\s\-\'\(\)]+$", name):
        return False, "Sequence name contains invalid characters"
    
    return True, ""

def validate_yoga_style(style: str) -> Tuple[bool, str]:
    """Validate yoga style selection."""
    valid_styles = {
        "hatha", "vinyasa", "yin", "restorative", "ashtanga", "bikram", 
        "hot", "power", "iyengar", "kundalini", "gentle", "beginner"
    }
    
    if not style or not style.strip():
        return False, "Yoga style must be selected"
    
    style_lower = style.strip().lower()
    if style_lower not in valid_styles:
        return False, f"Invalid yoga style. Valid options: {', '.join(sorted(valid_styles))}"
    
    return True, ""

def validate_sequence_data(sequence_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate complete sequence data structure."""
    required_fields = ["name", "duration", "flow"]
    
    # Check required fields exist
    for field in required_fields:
        if field not in sequence_data:
            return False, f"Missing required field: {field}"
    
    # Validate sequence name
    name_valid, name_error = validate_sequence_name(sequence_data["name"])
    if not name_valid:
        return False, f"Invalid sequence name: {name_error}"
    
    # Validate duration
    duration_valid, duration_error, _ = validate_duration(str(sequence_data["duration"]))
    if not duration_valid:
        return False, f"Invalid sequence duration: {duration_error}"
    
    # Validate flow is not empty
    flow = sequence_data.get("flow", [])
    if not flow or len(flow) == 0:
        return False, "Sequence must contain at least one pose"
    
    # Validate each pose in the flow
    for i, pose in enumerate(flow):
        if not isinstance(pose, dict):
            return False, f"Pose {i+1} must be a dictionary"
        
        if "name" not in pose:
            return False, f"Pose {i+1} missing required 'name' field"
        
        pose_name_valid, pose_name_error = validate_pose_name(pose["name"])
        if not pose_name_valid:
            return False, f"Pose {i+1} has invalid name: {pose_name_error}"
    
    return True, ""

def validate_new_pose_data(pose_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate all data for creating a new pose."""
    errors = []
    
    # Validate name
    name_valid, name_error = validate_pose_name(pose_data.get("name", ""))
    if not name_valid:
        errors.append(name_error)
    
    # Validate duration
    duration_valid, duration_error, _ = validate_duration(str(pose_data.get("default_duration", "")))
    if not duration_valid:
        errors.append(f"Duration: {duration_error}")
    
    # Validate difficulty
    difficulty_valid, difficulty_error, _ = validate_difficulty(str(pose_data.get("difficulty", "")))
    if not difficulty_valid:
        errors.append(f"Difficulty: {difficulty_error}")
    
    # Validate muscle groups
    muscles = pose_data.get("muscle_groups", [])
    if isinstance(muscles, str):
        muscles = [m.strip() for m in muscles.split(",") if m.strip()]
    
    muscles_valid, muscles_error = validate_muscle_groups(muscles)
    if not muscles_valid:
        errors.append(f"Muscle groups: {muscles_error}")
    
    return len(errors) == 0, errors

# Database-specific validation functions
def validate_pose_name_unique(pose_name: str, exclude_current: str = None) -> Tuple[bool, str]:
    """Check if pose name is unique in the database."""
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            if exclude_current:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM poses WHERE name = ? AND name != ?", 
                    (pose_name, exclude_current)
                )
            else:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM poses WHERE name = ?", 
                    (pose_name,)
                )
            
            result = cursor.fetchone()
            count = result["count"] if result else 0
            
            if count > 0:
                return False, f"Pose name '{pose_name}' already exists"
            
            return True, ""
            
    except Exception as e:
        logger.error(f"Error checking pose name uniqueness: {e}")
        return False, "Error validating pose name uniqueness"

def validate_flow_name_unique(flow_name: str, exclude_current: str = None) -> Tuple[bool, str]:
    """Check if flow name is unique in the database."""
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            if exclude_current:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM flows WHERE name = ? AND name != ?", 
                    (flow_name, exclude_current)
                )
            else:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM flows WHERE name = ?", 
                    (flow_name,)
                )
            
            result = cursor.fetchone()
            count = result["count"] if result else 0
            
            if count > 0:
                return False, f"Flow name '{flow_name}' already exists"
            
            return True, ""
            
    except Exception as e:
        logger.error(f"Error checking flow name uniqueness: {e}")
        return False, "Error validating flow name uniqueness"

# Updated database maintenance functions
def update_flow_durations() -> bool:
    """Update all flow durations based on their pose durations."""
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            # Get all flows
            cursor = conn.execute("SELECT id, name, flow_data FROM flows")
            flows = cursor.fetchall()
            
            updated_count = 0
            for flow in flows:
                try:
                    import json
                    flow_data = json.loads(flow["flow_data"]) if flow["flow_data"] else []
                    total_duration = sum(pose.get("duration", 0) for pose in flow_data)
                    
                    # Update the flow's duration
                    conn.execute(
                        "UPDATE flows SET duration = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (round(total_duration, 2), flow["id"])
                    )
                    updated_count += 1
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid flow data for flow: {flow['name']}")
                    continue
            
            logger.info(f"Updated durations for {updated_count} flows")
            return True
            
    except Exception as e:
        logger.error(f"Error updating flow durations: {e}")
        return False

def validate_database_integrity() -> Tuple[bool, List[str]]:
    """Check database for integrity issues."""
    issues = []
    
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            # Check for poses with invalid data
            cursor = conn.execute("SELECT name FROM poses WHERE name IS NULL OR name = ''")
            empty_pose_names = cursor.fetchall()
            for row in empty_pose_names:
                issues.append("Found pose with empty name")
            
            # Check for flows with invalid data
            cursor = conn.execute("SELECT name FROM flows WHERE name IS NULL OR name = ''")
            empty_flow_names = cursor.fetchall()
            for row in empty_flow_names:
                issues.append("Found flow with empty name")
            
            # Check for duplicate pose names
            cursor = conn.execute("""
                SELECT name, COUNT(*) as count 
                FROM poses 
                GROUP BY name 
                HAVING count > 1
            """)
            duplicate_poses = cursor.fetchall()
            for row in duplicate_poses:
                issues.append(f"Duplicate pose name: '{row['name']}' ({row['count']} instances)")
            
            # Check for duplicate flow names
            cursor = conn.execute("""
                SELECT name, COUNT(*) as count 
                FROM flows 
                GROUP BY name 
                HAVING count > 1
            """)
            duplicate_flows = cursor.fetchall()
            for row in duplicate_flows:
                issues.append(f"Duplicate flow name: '{row['name']}' ({row['count']} instances)")
            
            # Check for invalid difficulty levels
            cursor = conn.execute("SELECT name FROM poses WHERE difficulty < 1 OR difficulty > 5")
            invalid_difficulties = cursor.fetchall()
            for row in invalid_difficulties:
                issues.append(f"Pose '{row['name']}' has invalid difficulty level")
                
            logger.info(f"Database integrity check found {len(issues)} issues")
            
    except Exception as e:
        issues.append(f"Error during database integrity check: {e}")
        logger.error(f"Error checking database integrity: {e}")
    
    return len(issues) == 0, issues

def validate_favorites_integrity() -> Tuple[bool, List[str]]:
    """Check favorites for broken references to poses/flows."""
    issues = []
    
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            # Get all pose and flow names
            pose_cursor = conn.execute("SELECT name FROM poses")
            valid_pose_names = {row["name"] for row in pose_cursor.fetchall()}
            
            flow_cursor = conn.execute("SELECT name FROM flows")
            valid_flow_names = {row["name"] for row in flow_cursor.fetchall()}
            
            # Check favorites for broken references
            fav_cursor = conn.execute("SELECT id, name, type, favorite_data FROM favorites")
            favorites = fav_cursor.fetchall()
            
            for favorite in favorites:
                try:
                    import json
                    favorite_data = json.loads(favorite["favorite_data"]) if favorite["favorite_data"] else {}
                    
                    # Check poses in flows
                    if "flow" in favorite_data:
                        for pose in favorite_data["flow"]:
                            pose_name = pose.get("name")
                            if pose_name and pose_name not in valid_pose_names:
                                issues.append(f"Favorite '{favorite['name']}' references non-existent pose: '{pose_name}'")
                    
                    # Check direct favorites
                    if favorite["type"] == "pose":
                        pose_name = favorite["name"]
                        if pose_name and pose_name not in valid_pose_names:
                            issues.append(f"Favorited pose no longer exists: '{pose_name}'")
                    elif favorite["type"] == "flow":
                        flow_name = favorite["name"]
                        if flow_name and flow_name not in valid_flow_names:
                            issues.append(f"Favorited flow no longer exists: '{flow_name}'")
                            
                except json.JSONDecodeError:
                    issues.append(f"Favorite '{favorite['name']}' has invalid JSON data")
                    
        logger.info(f"Favorites integrity check found {len(issues)} issues")
        
    except Exception as e:
        issues.append(f"Error during favorites integrity check: {e}")
        logger.error(f"Error checking favorites integrity: {e}")
    
    return len(issues) == 0, issues

def cleanup_broken_favorites() -> bool:
    """Remove favorites that reference non-existent poses or flows."""
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            # Get valid names
            pose_cursor = conn.execute("SELECT name FROM poses")
            valid_pose_names = {row["name"] for row in pose_cursor.fetchall()}
            
            flow_cursor = conn.execute("SELECT name FROM flows")
            valid_flow_names = {row["name"] for row in flow_cursor.fetchall()}
            
            # Remove broken direct favorites
            pose_result = conn.execute(
                "DELETE FROM favorites WHERE type = 'pose' AND name NOT IN (SELECT name FROM poses)"
            )
            
            flow_result = conn.execute(
                "DELETE FROM favorites WHERE type = 'flow' AND name NOT IN (SELECT name FROM flows)"
            )
            
            removed_count = pose_result.rowcount + flow_result.rowcount
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} broken favorites")
            
            return True
            
    except Exception as e:
        logger.error(f"Error cleaning up broken favorites: {e}")
        return False