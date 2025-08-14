import re
import logging
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_pose_name(name: str) -> Tuple[bool, str]:
    #Validate pose name format and content.
    
    #Args:
    #    name: Pose name to validate
        
    #Returns:
    #    Tuple of (is_valid, error_message)
        
    #Example:
    #    valid, error = validate_pose_name("Mountain Pose")
    #    if not valid:
    #        print(f"Error: {error}")
    if not name or not name.strip():
        return False, "Pose name cannot be empty",""
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Pose name must be at least 2 characters long",""
    
    if len(name) > 100:
        return False, "Pose name is too long (maximum 100 characters)",""
    
    # Check for invalid characters (allow letters, numbers, spaces, apostrophes, hyphens)
    if not re.match(r"^[A-Za-z0-9\s\-\']+$", name):
        return False, "Pose name contains invalid characters. Only letters, numbers, spaces, hyphens, and apostrophes are allowed",""
    
    # Check for reasonable format (not all numbers or all spaces)
    if name.isdigit():
        return False, "Pose name cannot be only numbers",""
    
    if not re.search(r'[A-Za-z]', name):
        return False, "Pose name must contain at least one letter", ""
    
    if name == "Name Your Pose":
        return False, "Pose name cannot be the default placeholder 'Name Your Pose'", ""
    
    return True, "", name


def validate_duration(duration_str: str, min_duration: float = 0.1, max_duration: float = 600.0) -> Tuple[bool, str, float]:
    #Validate duration input and convert to float.
    
    #Args:
    #    duration_str: Duration as string
    #    min_duration: Minimum allowed duration in minutes
    #    max_duration: Maximum allowed duration in minutes
        
    #Returns:
    #    Tuple of (is_valid, error_message, converted_duration)
        
    #Example:
    #    valid, error, duration = validate_duration("5.5")
    #    if valid:
    #        print(f"Duration: {duration} minutes")
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
    #Validate difficulty level input.
    
    #Args:
    #    difficulty_str: Difficulty as string
    #    min_level: Minimum difficulty level
    #    max_level: Maximum difficulty level
        
    #Returns:
    #    Tuple of (is_valid, error_message, converted_difficulty)
        
    #Example:
    #    valid, error, difficulty = validate_difficulty("3")
    #    if valid:
    #        print(f"Difficulty level: {difficulty}")
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
    #Validate muscle group selections.
    
    #Args:
    #    muscle_list: List of muscle group names
        
    #Returns:
    #    Tuple of (is_valid, error_message)
        
    #Example:
    #    valid, error = validate_muscle_groups(["core", "arms"])
    #    if not valid:
    #        print(f"Invalid muscle groups: {error}")

    # Define valid muscle groups for yoga poses
    valid_muscles = {
        "core", "abs", "arms", "shoulders", "back", "legs", "thighs", "calves",
        "hips", "glutes", "hamstrings", "quadriceps", "pelvic_floor", 
        "full_body", "neck", "spine", "ankles", "wrists", "chest",
        "side_body", "groin", "hip_flexors"
    }
    
    if not muscle_list:
        return False, "At least one muscle group must be selected"
    
    # Check for empty or invalid entries
    cleaned_muscles = []
    for muscle in muscle_list:
        if isinstance(muscle, str) and muscle.strip():
            cleaned_muscles.append(muscle.strip().lower())
    
    if not cleaned_muscles:
        return False, "At least one valid muscle group must be selected",""
    
    # Check for invalid muscle groups
    invalid_muscles = [m for m in cleaned_muscles if m not in valid_muscles]
    if invalid_muscles:
        return False, f"Invalid muscle groups: {', '.join(invalid_muscles)}. Valid options include: {', '.join(sorted(valid_muscles))}",""
    
    return True, "",cleaned_muscles


def validate_sequence_name(name: str) -> Tuple[bool, str]:
    #Validate yoga sequence name.
    
    #Args:
    #    name: Sequence name to validate
        
    #Returns:
    #    Tuple of (is_valid, error_message)

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
    #Validate yoga style selection.
    
    #Args:
    #    style: Yoga style name
        
    #Returns:
    #    Tuple of (is_valid, error_message)
    
    valid_styles = {
        "hatha", "vinyasa", "yin", "restorative", "ashtanga", "bikram", 
        "hot", "power", "iyengar", "kundalini", "gentle", "beginner"
    }
    
    if style not in valid_styles or style.strip() not in valid_styles:
        return False, "Yoga style must be selected"
    
