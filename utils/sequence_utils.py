"""Sequence building utilities for GUMBY yoga app.

This module provides utilities for extracting data from flows,
filtering flows by criteria, and selecting optimal flow combinations.
"""

import logging
from typing import List, Dict, Any, Set, Tuple
from utils.file_utils import safe_load_json
from config import FLOWS_FILE

logger = logging.getLogger(__name__)


def extract_unique_values(flows_data: Dict[str, Any], field_path: str) -> List[str]:
    """Extract all unique values for a field from flows data.
    
    Args:
        flows_data: Complete flows data dictionary
        field_path: Dot notation path to field (e.g., "style", "muscle_groups")
        
    Returns:
        Sorted list of unique values
        
    Example:
        extract_unique_values(flows_data, "style") -> ["hatha", "vinyasa", "yin"]
        extract_unique_values(flows_data, "muscle_groups") -> ["arms", "core", "legs"]
    """
    unique_values: Set[str] = set()
    
    for flow in flows_data.get("flowing_sequences", {}).values():
        field_value = flow.get(field_path, [])
        
        # Handle both single values and lists
        if isinstance(field_value, list):
            unique_values.update(field_value)
        elif field_value:
            unique_values.add(field_value)
    
    return sorted(list(unique_values))


def filter_flows_by_criteria(flows: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter flows based on multiple criteria.
    
    Args:
        flows: List of flow dictionaries
        criteria: Dictionary of filtering criteria
        
    Returns:
        List of flows matching all criteria
        
    Example:
        criteria = {
            "style": ["vinyasa"],
            "difficulty_max": 3,
            "muscle_groups": ["core", "arms"]
        }
    """
    filtered_flows = []
    
    for flow in flows:
        matches_category_criteria = True
        matches_energy_criteria = True
        matches_muscle_criteria = True
        matches_tags_criteria = True
        
        # Check style matching
        if "style" in criteria:
            flow_styles = flow.get("style", [])
            required_styles = criteria["style"]
            if not any(style in flow_styles for style in required_styles):
                matches_style_criteria = False
                continue
        
        # Check category matching
        if "category" in criteria:
            if flow.get("category") not in criteria["category"]:
                matches_category_criteria = False
                continue
            else:
                matches_category_criteria = True
        
        # Check energy level matching
        if "energy_level" in criteria:
            if flow.get("energy_level") not in criteria["energy_level"]:
                matches_energy_criteria = False
                continue
            else:
                matches_energy_criteria = True
        
        # Check muscle group overlap
        if "muscle_groups" in criteria and criteria["muscle_groups"]:  # Add the second condition
            flow_muscles = flow.get("muscle_groups", [])
            required_muscles = criteria["muscle_groups"]
            if not any(muscle in flow_muscles for muscle in required_muscles):
                matches_muscle_criteria = False
                continue
            else:
                matches_muscle_criteria = True
        
        # Check tags overlap
        if "tags" in criteria:
            flow_tags = flow.get("tags", [])
            required_tags = criteria["tags"]
            if not any(tag in flow_tags for tag in required_tags):
                matches_tags_criteria = False
                continue
            else:
                matches_tags_criteria = True
        
        if matches_category_criteria or matches_energy_criteria or matches_muscle_criteria or matches_tags_criteria:
            filtered_flows.append(flow)
    
    return filtered_flows


def calculate_flow_compatibility_score(flow: Dict[str, Any], criteria: Dict[str, Any]) -> float:
    """Calculate how well a flow matches the given criteria.
    
    Args:
        flow: Flow dictionary
        criteria: Criteria dictionary with scoring preferences
        
    Returns:
        Compatibility score (0.0 to 1.0, higher is better)
        
    Example:
        criteria = {
            "target_muscles": ["core", "arms"],
            "preferred_energy": "building",
            "target_difficulty": 2
        }
    """
    score = 0.0
    max_score = 0.0
    
    # Score muscle group alignment
    if "target_muscles" in criteria:
        flow_muscles = set(flow.get("muscle_groups", []))
        target_muscles = set(criteria["target_muscles"])
        muscle_overlap = len(flow_muscles.intersection(target_muscles))
        muscle_score = muscle_overlap / len(target_muscles) if target_muscles else 0
        score += muscle_score * 0.4  # 40% weight
        max_score += 0.4
    
    # Score energy level match
    if "preferred_energy" in criteria:
        if flow.get("energy_level") == criteria["preferred_energy"]:
            score += 0.3  # 30% weight
        max_score += 0.3
    
    # Score difficulty proximity
    if "target_difficulty" in criteria:
        flow_difficulty = flow.get("difficulty", 2)
        target_difficulty = criteria["target_difficulty"]
        difficulty_diff = abs(flow_difficulty - target_difficulty)
        difficulty_score = max(0, 1 - (difficulty_diff / 3))  # Scale by max diff of 3
        score += difficulty_score * 0.2  # 20% weight
        max_score += 0.2
    
    # Score duration appropriateness
    if "target_duration" in criteria:
        flow_duration = flow.get("duration", 0)
        target_duration = criteria["target_duration"]
        if target_duration > 0:
            duration_ratio = min(flow_duration / target_duration, target_duration / flow_duration)
            score += duration_ratio * 0.1  # 10% weight
        max_score += 0.5
    
    return score / max_score if max_score > 0 else 0.0

import itertools

def select_best_flows_for_time(flows, target_time, tolerance=0.1):
    """Select combination of flows that best fits target time."""
    print(f"Target time: {target_time}, Tolerance: {tolerance}")
    
    if not flows:
        print("No flows provided!")
        return []
    
    min_time = target_time * (1 - tolerance)
    max_time = target_time * (1 + tolerance)
    print(f"Acceptable range: {min_time:.1f} - {max_time:.1f} minutes")
    
    best_combo = []
    best_total = 0

    # Try all combinations up to the number of flows (no repeats)
    for r in range(1, len(flows) + 1):
        for combo in itertools.combinations(flows, r):
            total = sum(f.get("duration", 0) for f in combo)
            
            if min_time <= total <= max_time and total > best_total:
                best_combo = list(combo)
                best_total = total
                print(f"    ✅ New best: {total}min")
                if best_total == max_time:
                    break

    # If best combo is still short, repeat flows to fill the gap
    selected = list(best_combo)
    total_time = sum(f.get("duration", 0) for f in selected)
    
    if total_time < min_time:
        flows_sorted = sorted(flows, key=lambda f: f.get("duration", 0), reverse=True)
        while total_time < min_time:
            for flow in flows_sorted:
                dur = flow.get("duration", 0)
                if total_time + dur <= max_time:
                    selected.append(flow)
                    total_time += dur
                    if total_time >= min_time:
                        break
            else:
                # If nothing fits, break to avoid infinite loop
                print("    No more flows fit, stopping")
                break
    
    final_total = sum(f.get("duration", 0) for f in selected)
    
    return selected

def load_class_template(style: str) -> Dict[str, Any]:
    """Load class structure template for given style.
    
    Args:
        style: Yoga style name (e.g., "vinyasa", "hatha")
        
    Returns:
        Template dictionary with structure rules
        
    Raises:
        KeyError: If style not found in templates
    """
    # First, load the templates data
    from config import CLASS_TEMPLATES_FILE
    templates_data = safe_load_json(CLASS_TEMPLATES_FILE, {"class_structure_templates": {}})
    templates = templates_data.get("class_structure_templates", {})
    
    # Check if style exists
    if style.lower() not in templates:
        available_styles = list(templates.keys())
        raise KeyError(f"Style '{style}' not found. Available styles: {available_styles}")
    
    # Return the template for the style
    return templates[style.lower()]


def get_available_styles() -> List[str]:
    """Get list of all available class styles.
    
    Returns:
        Sorted list of available style names
    """
    sequences_data = safe_load_json(FLOWS_FILE, {"flowing_sequences": {}})
    return sorted(sequences_data.get("class_structure_templates", {}).keys())


def calculate_section_durations(total_duration: float, template: Dict[str, Any]) -> Dict[str, float]:
    """Calculate duration for each class section based on template percentages."""
    
    # Your templates use individual percentage fields, not structure/ratios
    section_durations = {
        "warm_up": total_duration * template.get("warm_up_percentage", 0.25),
        "main_flow": total_duration * template.get("main_flow_percentage", 0.5), 
        "cool_down": total_duration * template.get("cool_down_percentage", 0.25)
    }
    
    return section_durations


def group_flows_by_category(flows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group flows by their category.
    
    Args:
        flows: List of flow dictionaries
        
    Returns:
        Dictionary mapping categories to lists of flows
        
    Example:
        group_flows_by_category(flows)
        # Returns: {"warm_up": [...], "main_flow": [...], "cool_down": [...]}
    """
    grouped = {}
    
    for flow in flows:
        category = flow.get("category", "uncategorized")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(flow)
    
    return grouped


def select_flows_for_sequence(user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Main function to select flows for a complete yoga sequence.
    Args:
        user_preferences: Dictionary with user's requirements
            - duration: Total class duration in minutes
            - style: Yoga style (vinyasa, hatha, yin)
            - muscle_groups: List of target muscle groups
            - difficulty: Preferred difficulty level (1-5) 
    Returns:
        List of selected flows forming a complete sequence
    Example:
        preferences = {
            "duration": 60,
            "style": "vinyasa", 
            "muscle_groups": ["core", "arms"],
            "difficulty": 2
        }
        flows = select_flows_for_sequence(preferences)
    """
    # Load sequences data
    from utils.file_utils import load_flows_data
    sequences_data = load_flows_data()
    all_flows = list(sequences_data.get("flowing_sequences", {}).values())
    
    if not all_flows:
        logger.warning("No flows available for sequence generation")
        return []
    
    # Get class template for the style
    try:
        template = load_class_template(user_preferences["style"])
    except KeyError:
        logger.error(f"Unknown style: {user_preferences['style']}")
        return []
    
    # Calculate time allocation for each section
    section_durations = calculate_section_durations(user_preferences["duration"], template)
    
    # Filter flows by user criteria
    filter_criteria = {
        "style": [user_preferences["style"]],
        "muscle_groups": user_preferences.get("muscle_groups", []),
        "difficulty_max": user_preferences.get("difficulty", 5)
    }
    
    suitable_flows = filter_flows_by_criteria(all_flows, filter_criteria)

    print(f"❗ Filtering result: {len(suitable_flows)} flows")

    # Group flows by category
    flows_by_category = group_flows_by_category(suitable_flows)
    print(f"🔍 Grouped by category: {list(flows_by_category.keys())}")
    for category, flows in flows_by_category.items():
        print(f"  {category}: {len(flows)} flows")
    
    # Group flows by category
    flows_by_category = group_flows_by_category(suitable_flows)
    
    # Select flows for each section
    selected_flows = []
    
    for section_name, section_duration in section_durations.items():
        # Map section names to flow categories
        category_mapping = {
            "warm_up": "warm_up",
            "main_flow": ["standing_flow", "seated_flow", "hip_opener", "backbend_flow","main_flow","energizing_flow","therapeutic","arm_balance","twist_flow","inversion",],
            "cool_down": "cool_down"
        }
        
        target_categories = category_mapping.get(section_name, [section_name])
        if isinstance(target_categories, str):
            target_categories = [target_categories]
        
        # Collect available flows for this section
        section_flows = []
        for category in target_categories:
            section_flows.extend(flows_by_category.get(category, []))

        print(f"Section '{section_name}' candidate flows: {[f.get('name') for f in section_flows]}")
        
        if section_flows:
            # Select best flows for this section's time allocation
            section_selected = select_best_flows_for_time(section_flows, section_duration, tolerance=0.2) 
            selected_flows.extend(section_selected)
        else:
            logger.warning(f"No flows available for section: {section_name}")
    
    logger.info(f"Generated sequence with {len(selected_flows)} flows")
    return selected_flows


def validate_sequence_structure(flows: List[Dict[str, Any]], template: Dict[str, Any]) -> Tuple[bool, List[str]]:
    issues = []
    
    if not flows:
        issues.append("Sequence cannot be empty")
        return False, issues
    
    # Check if we have flows for each required section
    required_sections = template.get("structure", [])
    flows_by_category = group_flows_by_category(flows)
    
    for section in required_sections:
        if section not in flows_by_category:
            issues.append(f"Missing flows for required section: {section}")
    
    # Check total duration reasonableness
    total_duration = sum(flow.get("duration", 0) for flow in flows)
    if total_duration < 5:
        issues.append("Total sequence duration too short (less than 5 minutes)")
    elif total_duration > 120:
        issues.append("Total sequence duration too long (more than 2 hours)")
    
    # Check for style consistency
    styles_in_sequence = set()
    for flow in flows:
        flow_styles = flow.get("style", [])
        styles_in_sequence.update(flow_styles)
    
    if len(styles_in_sequence) > 2:
        issues.append(f"Too many different styles in sequence: {list(styles_in_sequence)}")
    
    return len(issues) == 0, issues


def optimize_sequence_order(flows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Optimize the order of flows within a sequence for better flow.
    
    Args:
        flows: List of flows to reorder
        
    Returns:
        Reordered list of flows
        
    Note:
        This implements a simple ordering based on energy levels and categories.
        More sophisticated ordering could consider pose transitions.
    """
    if len(flows) <= 1:
        return flows
    
    # Define energy level order for optimal class progression
    energy_order = {
        "calming": 1,
        "building": 2, 
        "energizing": 3,
        "peak": 4,
        "releasing": 5,
        "deeply_relaxing": 6
    }
    
    # Define category order
    category_order = {
        "warm_up": 1,
        "standing_flow": 2,
        "seated_flow": 3,
        "hip_opener": 4,
        "backbend_flow": 5,
        "cool_down": 6
    }
    
    def get_sort_key(flow):
        category_score = category_order.get(flow.get("category", ""), 3)
        energy_score = energy_order.get(flow.get("energy_level", ""), 3)
        return (category_score, energy_score)
    
    optimized_flows = sorted(flows, key=get_sort_key)
    
    logger.info(f"Optimized sequence order for {len(flows)} flows")
    return optimized_flows


# Convenience functions for common operations
def get_flow_summary(flow: Dict[str, Any]) -> str:
    """Get a brief summary of a flow for display purposes."""
    name = flow.get("name", "Unnamed Flow")
    duration = flow.get("duration", 0)
    difficulty = flow.get("difficulty", "Unknown")
    return f"{name} ({duration}min, Level {difficulty})"


def calculate_total_sequence_duration(flows: List[Dict[str, Any]]) -> float:
    """Calculate total duration of a sequence."""
    return sum(flow.get("duration", 0) for flow in flows)


def get_sequence_muscle_groups(flows: List[Dict[str, Any]]) -> List[str]:
    """Get all muscle groups targeted by a sequence."""
    all_muscles = set()
    for flow in flows:
        muscles = flow.get("muscle_groups", [])
        all_muscles.update(muscles)
    return sorted(list(all_muscles))