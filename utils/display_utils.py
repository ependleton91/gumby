"""Display formatting utilities for GUMBY yoga app.

This module provides consistent text formatting between internal data format
and user-friendly display format without changing the underlying words.
"""

from typing import List


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
    formatted_muscles = format_list_for_display(muscle_groups)
    return ", ".join(formatted_muscles)


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
    formatted_styles = format_list_for_display(styles)
    return ", ".join(formatted_styles)