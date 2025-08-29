from typing import List, Dict
import functools

# Cache for expensive string operations
_format_cache: Dict[str, str] = {}
_cache_max_size = 1000

def _manage_cache():
    """Keep cache size reasonable."""
    if len(_format_cache) > _cache_max_size:
        # Remove oldest half of entries (simple cleanup)
        keys_to_remove = list(_format_cache.keys())[:-(_cache_max_size // 2)]
        for key in keys_to_remove:
            del _format_cache[key]

@functools.lru_cache(maxsize=256)
def format_for_display(internal_text: str) -> str:
    """Convert internal text format to user-friendly display format.
    
    Args:
        internal_text: Text in internal format (e.g., "full_body", "pelvic_floor")
        
    Returns:
        Text formatted for display (e.g., "Full Body", "Pelvic Floor")
        
    Example:
        format_for_display("full_body") -> "Full Body"
        format_for_display("pelvic_floor") -> "Pelvic Floor"
        format_for_display("vinyasa") -> "Vinyasa"
    """
    if not internal_text:
        return ""
    
    return internal_text.replace("_", " ").title()

@functools.lru_cache(maxsize=256)
def format_for_internal(display_text: str) -> str:
    """Convert display text back to internal format.
    
    Args:
        display_text: Text in display format (e.g., "Full Body", "Pelvic Floor")
        
    Returns:
        Text in internal format (e.g., "full_body", "pelvic_floor")
        
    Example:
        format_for_internal("Full Body") -> "full_body"
        format_for_internal("Pelvic Floor") -> "pelvic_floor"
        format_for_internal("Vinyasa") -> "vinyasa"
    """
    if not display_text:
        return ""
    
    return display_text.lower().replace(" ", "_")

def format_list_for_display(internal_list: List[str]) -> List[str]:
    """Convert list of internal strings to display format.
    
    Args:
        internal_list: List of strings in internal format
        
    Returns:
        List of strings formatted for display
        
    Example:
        format_list_for_display(["core", "full_body", "pelvic_floor"])
        -> ["Core", "Full Body", "Pelvic Floor"]
    """
    if not internal_list:
        return []
    
    return [format_for_display(item) for item in internal_list]

def format_list_for_internal(display_list: List[str]) -> List[str]:
    """Convert list of display strings back to internal format.
    
    Args:
        display_list: List of strings in display format
        
    Returns:
        List of strings in internal format
        
    Example:
        format_list_for_internal(["Core", "Full Body", "Pelvic Floor"])
        -> ["core", "full_body", "pelvic_floor"]
    """
    if not display_list:
        return []
        
    return [format_for_internal(item) for item in display_list]

def format_muscle_groups_display(muscle_groups: List[str]) -> str:
    """Format muscle groups list for display in UI.
    
    Args:
        muscle_groups: List of muscle group names in internal format
        
    Returns:
        Comma-separated string of formatted muscle groups
        
    Example:
        format_muscle_groups_display(["core", "arms", "full_body"])
        -> "Core, Arms, Full Body"
    """
    if not muscle_groups:
        return ""
        
    # Cache key for this specific list
    cache_key = f"muscles::{','.join(sorted(muscle_groups))}"
    
    if cache_key in _format_cache:
        return _format_cache[cache_key]
    
    formatted_muscles = format_list_for_display(muscle_groups)
    result = ", ".join(formatted_muscles)
    
    # Cache the result
    _format_cache[cache_key] = result
    _manage_cache()
    
    return result

def format_style_list_display(styles: List[str]) -> str:
    """Format style list for display in UI.
    
    Args:
        styles: List of style names in internal format
        
    Returns:
        Comma-separated string of formatted styles
        
    Example:
        format_style_list_display(["vinyasa", "hatha"])
        -> "Vinyasa, Hatha"
    """
    if not styles:
        return ""
        
    # Cache key for this specific list
    cache_key = f"styles::{','.join(sorted(styles))}"
    
    if cache_key in _format_cache:
        return _format_cache[cache_key]
    
    formatted_styles = format_list_for_display(styles)
    result = ", ".join(formatted_styles)
    
    # Cache the result
    _format_cache[cache_key] = result
    _manage_cache()
    
    return result

# Additional utility functions for common UI formatting needs

def format_duration_display(minutes: float) -> str:
    """Format duration for user display.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string
        
    Example:
        format_duration_display(90.5) -> "1h 30m"
        format_duration_display(5.25) -> "5m"
    """
    if minutes <= 0:
        return "0m"
    
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    
    if hours > 0:
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        else:
            return f"{hours}h"
    else:
        return f"{remaining_minutes}m"

def format_difficulty_display(difficulty: int) -> str:
    """Format difficulty level for display.
    
    Args:
        difficulty: Difficulty level (1-5)
        
    Returns:
        Formatted difficulty string
        
    Example:
        format_difficulty_display(1) -> "Beginner"
        format_difficulty_display(5) -> "Expert"
    """
    difficulty_map = {
        1: "Beginner",
        2: "Easy",
        3: "Intermediate", 
        4: "Advanced",
        5: "Expert"
    }
    
    return difficulty_map.get(difficulty, "Unknown")

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text for display with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    if len(suffix) >= max_length:
        return text[:max_length]
    
    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix

def format_list_with_limit(items: List[str], max_items: int = 3, 
                          format_func=format_for_display) -> str:
    """Format list for display with item limit.
    
    Args:
        items: List of items to format
        max_items: Maximum items to show
        format_func: Function to format individual items
        
    Returns:
        Formatted string with "and X more" if needed
        
    Example:
        format_list_with_limit(["core", "arms", "legs", "back"], 2)
        -> "Core, Arms, and 2 more"
    """
    if not items:
        return ""
    
    if len(items) <= max_items:
        formatted_items = [format_func(item) for item in items]
        return ", ".join(formatted_items)
    
    # Show first max_items and add "and X more"
    shown_items = [format_func(item) for item in items[:max_items]]
    remaining_count = len(items) - max_items
    
    result = ", ".join(shown_items)
    result += f", and {remaining_count} more"
    
    return result

# Clear caches function for memory management
def clear_display_caches():
    """Clear all display formatting caches."""
    global _format_cache
    _format_cache.clear()
    
    # Clear lru_cache for the decorated functions
    format_for_display.cache_clear()
    format_for_internal.cache_clear()

# Get cache statistics
def get_display_cache_stats() -> Dict[str, int]:
    """Get cache statistics for monitoring."""
    return {
        "format_cache_size": len(_format_cache),
        "display_cache_hits": format_for_display.cache_info().hits,
        "display_cache_misses": format_for_display.cache_info().misses,
        "internal_cache_hits": format_for_internal.cache_info().hits,
        "internal_cache_misses": format_for_internal.cache_info().misses,
    }