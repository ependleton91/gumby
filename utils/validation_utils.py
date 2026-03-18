import re
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_pose_name(name: str) -> Tuple[bool, str]:
    """Validate pose name format and content.
    
    Args:
        name: Pose name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        valid, error = validate_pose_name("Mountain Pose")
        if not valid:
            print(f"Error: {error}")
    """
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
    """Validate duration input and convert to float.
    
    Args:
        duration_str: Duration as string
        min_duration: Minimum allowed duration in minutes
        max_duration: Maximum allowed duration in minutes
        
    Returns:
        Tuple of (is_valid, error_message, converted_duration)
        
    Example:
        valid, error, duration = validate_duration("5.5")
        if valid:
            print(f"Duration: {duration} minutes")
    """
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
    """Validate difficulty level input.
    
    Args:
        difficulty_str: Difficulty as string
        min_level: Minimum difficulty level
        max_level: Maximum difficulty level
        
    Returns:
        Tuple of (is_valid, error_message, converted_difficulty)
        
    Example:
        valid, error, difficulty = validate_difficulty("3")
        if valid:
            print(f"Difficulty level: {difficulty}")
    """
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
    """Validate muscle group selections using database lookup.
    
    Args:
        muscle_list: List of muscle group names
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        valid, error = validate_muscle_groups(["core", "arms"])
        if not valid:
            print(f"Invalid muscle groups: {error}")
    """
    if not muscle_list:
        return False, "At least one muscle group must be selected"
    
    # Check for empty or invalid entries
    cleaned_muscles = []
    for muscle in muscle_list:
        if isinstance(muscle, str) and muscle.strip():
            cleaned_muscles.append(muscle.strip().lower())
    
    if not cleaned_muscles:
        return False, "At least one valid muscle group must be selected"
    
    # Get valid muscle groups from database
    try:
        from utils.database_utils import get_all_muscle_groups
        valid_muscles = {mg.lower() for mg in get_all_muscle_groups()}
        
        # If no muscle groups in database, use default set
        if not valid_muscles:
            valid_muscles = {
                "core", "abs", "arms", "shoulders", "back", "legs", "thighs", "calves",
                "hips", "glutes", "hamstrings", "quadriceps", "pelvic_floor", 
                "full_body", "neck", "spine", "ankles", "wrists", "chest",
                "side_body", "groin", "hip_flexors"
            }
    except ImportError:
        # Fallback if database not available
        valid_muscles = {
            "core", "abs", "arms", "shoulders", "back", "legs", "thighs", "calves",
            "hips", "glutes", "hamstrings", "quadriceps", "pelvic_floor", 
            "full_body", "neck", "spine", "ankles", "wrists", "chest",
            "side_body", "groin", "hip_flexors"
        }
    
    # Check for invalid muscle groups
    invalid_muscles = [m for m in cleaned_muscles if m not in valid_muscles]
    if invalid_muscles:
        return False, f"Invalid muscle groups: {', '.join(invalid_muscles)}. Valid options include: {', '.join(sorted(valid_muscles))}"
    
    return True, ""


def validate_sequence_name(name: str) -> Tuple[bool, str]:
    """Validate yoga sequence name.
    
    Args:
        name: Sequence name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
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
    """Validate yoga style selection using database lookup.
    
    Args:
        style: Yoga style name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not style or not style.strip():
        return False, "Yoga style must be selected"
    
    try:
        from utils.database_utils import get_all_yoga_styles
        valid_styles = {s.lower() for s in get_all_yoga_styles()}
        
        # If no styles in database, use default set
        if not valid_styles:
            valid_styles = {
                "hatha", "vinyasa", "yin", "restorative", "ashtanga", "bikram", 
                "hot", "power", "iyengar", "kundalini", "gentle", "beginner"
            }
    except ImportError:
        # Fallback if database not available
        valid_styles = {
            "hatha", "vinyasa", "yin", "restorative", "ashtanga", "bikram", 
            "hot", "power", "iyengar", "kundalini", "gentle", "beginner"
        }
    
    style_lower = style.strip().lower()
    if style_lower not in valid_styles:
        return False, f"Invalid yoga style. Valid options: {', '.join(sorted(valid_styles))}"
    
    return True, ""


def validate_sequence_data(sequence_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate complete sequence data structure.
    
    Args:
        sequence_data: Dictionary containing sequence information
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        valid, error = validate_sequence_data({
            "name": "Morning Flow",
            "duration": 30,
            "flow": [{"name": "Mountain Pose", "duration": 1}]
        })
    """
    required_fields = ["name", "duration"]
    
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
    
    # Validate flow if present (optional for some sequence types)
    flow = sequence_data.get("flow", [])
    if flow:
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
    """Validate all data for creating a new pose.
    
    Args:
        pose_data: Dictionary with pose information
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate name
    name_valid, name_error = validate_pose_name(pose_data.get("name", ""))
    if not name_valid:
        errors.append(name_error)
    
    # Check for unique name in database
    try:
        name_unique, unique_error = validate_pose_name_unique(pose_data.get("name", ""))
        if not name_unique:
            errors.append(unique_error)
    except Exception as e:
        logger.warning(f"Could not check pose name uniqueness: {e}")
    
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


def validate_new_flow_data(flow_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate all data for creating a new flow.
    
    Args:
        flow_data: Dictionary with flow information
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate name
    name_valid, name_error = validate_sequence_name(flow_data.get("name", ""))
    if not name_valid:
        errors.append(name_error)
    
    # Check for unique name in database
    try:
        name_unique, unique_error = validate_flow_name_unique(flow_data.get("name", ""))
        if not name_unique:
            errors.append(unique_error)
    except Exception as e:
        logger.warning(f"Could not check flow name uniqueness: {e}")
    
    # Validate duration
    duration_valid, duration_error, _ = validate_duration(str(flow_data.get("duration", "")))
    if not duration_valid:
        errors.append(f"Duration: {duration_error}")
    
    # Validate difficulty
    difficulty_valid, difficulty_error, _ = validate_difficulty(str(flow_data.get("difficulty", "")))
    if not difficulty_valid:
        errors.append(f"Difficulty: {difficulty_error}")
    
    # Validate styles
    styles = flow_data.get("style", [])
    if isinstance(styles, str):
        styles = [s.strip() for s in styles.split(",") if s.strip()]
    
    for style in styles:
        style_valid, style_error = validate_yoga_style(style)
        if not style_valid:
            errors.append(f"Style: {style_error}")
            break
    
    # Validate muscle groups
    muscles = flow_data.get("muscle_groups", [])
    if isinstance(muscles, str):
        muscles = [m.strip() for m in muscles.split(",") if m.strip()]
    
    if muscles:  # Muscle groups are optional for flows
        muscles_valid, muscles_error = validate_muscle_groups(muscles)
        if not muscles_valid:
            errors.append(f"Muscle groups: {muscles_error}")
    
    return len(errors) == 0, errors


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


def validate_database_integrity() -> Tuple[bool, List[str]]:
    """Check normalized database for integrity issues."""
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
            
            # Check for invalid difficulty levels
            cursor = conn.execute("SELECT name FROM poses WHERE difficulty < 1 OR difficulty > 5")
            invalid_difficulties = cursor.fetchall()
            for row in invalid_difficulties:
                issues.append(f"Pose '{row['name']}' has invalid difficulty level")
            
            # Check for orphaned muscle group relationships
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM pose_muscle_groups pmg
                LEFT JOIN poses p ON pmg.pose_id = p.id
                WHERE p.id IS NULL
            """)
            orphaned_pose_muscles = cursor.fetchone()["count"]
            if orphaned_pose_muscles > 0:
                issues.append(f"Found {orphaned_pose_muscles} orphaned pose-muscle relationships")
            
            # Check for orphaned flow relationships
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM flow_poses fp
                LEFT JOIN flows f ON fp.flow_id = f.id
                LEFT JOIN poses p ON fp.pose_id = p.id
                WHERE f.id IS NULL OR p.id IS NULL
            """)
            orphaned_flow_poses = cursor.fetchone()["count"]
            if orphaned_flow_poses > 0:
                issues.append(f"Found {orphaned_flow_poses} orphaned flow-pose relationships")
                
            logger.info(f"Database integrity check found {len(issues)} issues")
            
    except Exception as e:
        issues.append(f"Error during database integrity check: {e}")
        logger.error(f"Error checking database integrity: {e}")
    
    return len(issues) == 0, issues


def cleanup_orphaned_relationships() -> bool:
    """Remove orphaned relationships from junction tables."""
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            # Clean up orphaned pose-muscle relationships
            pose_muscle_result = conn.execute("""
                DELETE FROM pose_muscle_groups 
                WHERE pose_id NOT IN (SELECT id FROM poses)
                   OR muscle_group_id NOT IN (SELECT id FROM muscle_groups)
            """)
            
            # Clean up orphaned flow-pose relationships
            flow_pose_result = conn.execute("""
                DELETE FROM flow_poses 
                WHERE flow_id NOT IN (SELECT id FROM flows)
                   OR pose_id NOT IN (SELECT id FROM poses)
            """)
            
            # Clean up orphaned flow-style relationships
            flow_style_result = conn.execute("""
                DELETE FROM flow_styles 
                WHERE flow_id NOT IN (SELECT id FROM flows)
                   OR style_id NOT IN (SELECT id FROM yoga_styles)
            """)
            
            # Clean up orphaned flow-muscle relationships
            flow_muscle_result = conn.execute("""
                DELETE FROM flow_muscle_groups 
                WHERE flow_id NOT IN (SELECT id FROM flows)
                   OR muscle_group_id NOT IN (SELECT id FROM muscle_groups)
            """)
            
            total_removed = (pose_muscle_result.rowcount + flow_pose_result.rowcount + 
                           flow_style_result.rowcount + flow_muscle_result.rowcount)
            
            if total_removed > 0:
                logger.info(f"Cleaned up {total_removed} orphaned relationships")
            
            return True
            
    except Exception as e:
        logger.error(f"Error cleaning up orphaned relationships: {e}")
        return False


def validate_flow_pose_sequence(flow_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate that all poses in a flow exist in the database.
    
    Args:
        flow_data: Flow data containing pose sequence
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            # Get all valid pose names
            cursor = conn.execute("SELECT name FROM poses")
            valid_pose_names = {row["name"] for row in cursor.fetchall()}
            
            # Check each pose in the flow
            flow_poses = flow_data.get("flow", [])
            for i, pose in enumerate(flow_poses):
                pose_name = pose.get("name", "")
                
                if not pose_name:
                    errors.append(f"Pose {i+1} has no name")
                elif pose_name not in valid_pose_names:
                    errors.append(f"Pose '{pose_name}' does not exist in database")
                
                # Validate pose duration if specified
                if "duration" in pose:
                    duration_valid, duration_error, _ = validate_duration(str(pose["duration"]))
                    if not duration_valid:
                        errors.append(f"Pose {i+1} ({pose_name}): {duration_error}")
                        
    except Exception as e:
        errors.append(f"Error validating flow poses: {e}")
        
    return len(errors) == 0, errors


def validate_sequence_completeness(sequence_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate that a sequence has proper structure and content.
    
    Args:
        sequence_data: Complete sequence data
        
    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []
    
    # Check for balanced sequence structure
    flows = sequence_data.get("flows", {})
    if isinstance(flows, dict):
        has_warmup = "warm_up" in flows and len(flows["warm_up"]) > 0
        has_main = "main_flow" in flows and len(flows["main_flow"]) > 0
        has_cooldown = "cool_down" in flows and len(flows["cool_down"]) > 0
        
        if not has_warmup:
            warnings.append("Sequence has no warm-up flows")
        if not has_main:
            warnings.append("Sequence has no main flows")
        if not has_cooldown:
            warnings.append("Sequence has no cool-down flows")
    
    # Check duration reasonableness
    total_duration = sequence_data.get("total_duration", 0)
    if total_duration < 5:
        warnings.append("Sequence duration very short (less than 5 minutes)")
    elif total_duration > 120:
        warnings.append("Sequence duration very long (more than 2 hours)")
    
    # Check difficulty progression
    difficulty = sequence_data.get("difficulty", 1)
    if difficulty > 4:
        warnings.append("High difficulty sequence - ensure proper warm-up")
    
    return True, warnings  # Always return True as these are warnings, not errors


def recalculate_flow_duration_from_poses(flow_id: int) -> bool:
    """Recalculate and update flow duration based on pose durations."""
    try:
        from utils.database_utils import get_db_manager
        
        db = get_db_manager()
        with db.get_connection() as conn:
            # Get pose durations for this flow
            cursor = conn.execute("""
                SELECT COALESCE(fp.pose_duration, p.default_duration) as effective_duration
                FROM flow_poses fp
                JOIN poses p ON fp.pose_id = p.id
                WHERE fp.flow_id = ?
            """, (flow_id,))
            
            durations = [row["effective_duration"] for row in cursor.fetchall()]
            total_duration = sum(durations) if durations else 0.0
            
            # Update flow duration
            conn.execute(
                "UPDATE flows SET duration = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (total_duration, flow_id)
            )
            
            logger.info(f"Recalculated flow {flow_id} duration: {total_duration} minutes")
            return True
            
    except Exception as e:
        logger.error(f"Error recalculating flow duration: {e}")
        return False


def bulk_validate_poses() -> Tuple[int, int, List[str]]:
    """Validate all poses in database and return statistics.
    
    Returns:
        Tuple of (valid_count, invalid_count, error_list)
    """
    try:
        from utils.database_utils import get_all_poses
        
        poses = get_all_poses()
        valid_count = 0
        invalid_count = 0
        all_errors = []
        
        for pose in poses:
            valid, errors = validate_new_pose_data(pose)
            if valid:
                valid_count += 1
            else:
                invalid_count += 1
                all_errors.extend([f"Pose '{pose.get('name', 'Unknown')}': {error}" for error in errors])
        
        return valid_count, invalid_count, all_errors
        
    except Exception as e:
        logger.error(f"Error in bulk pose validation: {e}")
        return 0, 0, [f"Bulk validation failed: {e}"]


def bulk_validate_flows() -> Tuple[int, int, List[str]]:
    """Validate all flows in database and return statistics.
    
    Returns:
        Tuple of (valid_count, invalid_count, error_list)
    """
    try:
        from utils.database_utils import get_all_flows
        
        flows = get_all_flows()
        valid_count = 0
        invalid_count = 0
        all_errors = []
        
        for flow in flows:
            valid, errors = validate_new_flow_data(flow)
            if valid:
                valid_count += 1
            else:
                invalid_count += 1
                all_errors.extend([f"Flow '{flow.get('name', 'Unknown')}': {error}" for error in errors])
        
        return valid_count, invalid_count, all_errors
        
    except Exception as e:
        logger.error(f"Error in bulk flow validation: {e}")
        return 0, 0, [f"Bulk validation failed: {e}"]