
from .file_utils import (
    ensure_directory_exists,
    load_flows_data, load_poses_data, load_favorite_poses, load_favorite_flows, load_favorite_sequences, 
    update_favorites_after_pose_change, remove_pose_from_favorites, remove_sequence_from_favorites, remove_flow_from_favorites
)

from .image_utils import (
    ImageCache, get_image_preloader,
    standardize_pose_name_to_filename, load_pose_image, load_image_from_path,
    scale_image_for_display, create_placeholder_image, validate_image_file, 
    clear_image_cache, load_thumbnail_image, load_preview_image, load_carousel_image,
    preload_common_poses, get_cache_stats, optimize_cache_for_memory
)

from .validation_utils import (
    validate_pose_name, validate_duration, validate_difficulty,
    validate_muscle_groups, validate_sequence_name, validate_yoga_style,
    validate_sequence_data, validate_new_pose_data, validate_new_flow_data,
    validate_pose_name_unique, validate_flow_name_unique,
    validate_database_integrity, cleanup_orphaned_relationships,
    validate_flow_pose_sequence, validate_sequence_completeness,
    recalculate_flow_duration_from_poses, bulk_validate_poses, bulk_validate_flows
)

from .ui_utils import (
    hide_widgets, show_widgets, enable_widgets, disable_widgets, batch_widget_operations,
    toggle_widget_visibility, clear_layout, fade_out_widget, fade_in_widget,
    show_error_message, show_warning_message, show_info_message, 
    show_success_message, confirm_action, confirm_destructive_action,
    center_widget_on_screen, center_widget_on_parent, set_widget_loading_state, 
    create_separator_line, show_pose_validation_errors, confirm_sequence_delete, 
    confirm_pose_delete, show_save_success, ProgressDialog, clear_ui_caches
)

from .datetime_utils import (
    get_current_timestamp, get_current_date, get_current_time,
    format_duration_minutes, format_duration_seconds, 
    parse_timestamp, format_practice_duration, calculate_session_duration,
    format_time_ago, format_timer_display, parse_duration_input,
    is_recent_timestamp, get_practice_session_summary,
    get_practice_date_display, get_sequence_age_display
)

from .display_utils import (
    format_for_display, format_for_internal,
    format_list_for_display, format_list_for_internal,
    format_muscle_groups_display, format_style_list_display,
    format_duration_display, format_difficulty_display,
    truncate_text, format_list_with_limit,
    clear_display_caches, get_display_cache_stats
)

from .sequence_utils import (
    extract_unique_values, filter_flows_by_criteria,
    calculate_flow_compatibility_score, select_best_flows_for_time,
    load_class_template, get_available_styles, calculate_section_durations,
    group_flows_by_category, select_flows_for_sequence,
    validate_sequence_structure, optimize_sequence_order,
    get_flow_summary, calculate_total_sequence_duration, get_sequence_muscle_groups
)

# Import database utilities for direct use
from .database_utils import (
    # Core database management
    get_db_manager, DatabaseManager,
    
    # Lookup table helpers
    ensure_muscle_group_exists, ensure_yoga_style_exists,
    get_all_muscle_groups, get_all_yoga_styles,
    
    # Pose operations
    create_pose, get_pose_by_name, get_all_poses, update_pose, delete_pose,
    
    # Flow operations  
    create_flow, get_all_flows, update_flow, delete_flow, get_flow_with_full_poses,get_flow_by_name,
    
    # Sequence operations
    create_sequence, get_all_sequences,get_sequence_by_name,get_sequence_with_full_flows,
    
    # Favorites operations
    create_favorite, get_favorite_flows,get_favorite_poses,get_favorite_sequences, delete_favorite, get_favorite_by_name,
    
    # Practice session operations
    create_practice_session, get_practice_sessions,
)

# Version info for compatibility checking
__version__ = "2.0.0"  # Database-integrated version

# Convenience functions for common operations
def get_all_data():
    """Get all poses, flows, sequences, and favorites from database."""
    return {
        "poses": get_all_poses(),
        "flows": get_all_flows(), 
        "sequences": get_all_sequences(),
        "favorite flows": get_favorite_flows(),
        "favorite poses": get_favorite_poses(),
        "favorite sequences": get_favorite_sequences()
    }

def validate_all_data():
    """Run comprehensive validation on all database data."""
    poses_valid, poses_invalid, pose_errors = bulk_validate_poses()
    flows_valid, flows_invalid, flow_errors = bulk_validate_flows()
    db_valid, db_errors = validate_database_integrity()
    
    return {
        "poses": {"valid": poses_valid, "invalid": poses_invalid, "errors": pose_errors},
        "flows": {"valid": flows_valid, "invalid": flows_invalid, "errors": flow_errors},
        "database": {"valid": db_valid, "errors": db_errors},
        "overall_valid": db_valid and poses_invalid == 0 and flows_invalid == 0
    }

def cleanup_all_caches():
    """Clear all utility caches to free memory."""
    clear_image_cache()
    clear_display_caches() 
    clear_ui_caches()

def get_system_stats():
    """Get statistics about cache usage and system state."""
    return {
        "image_cache": get_cache_stats(),
        "display_cache": get_display_cache_stats(),
        "database_connected": get_db_manager() is not None
    }

# Export commonly used combinations
__all__ = [
    # File operations
    "ensure_directory_exists", "export_database_to_json",
    
    # Database operations
    "get_db_manager", "create_pose", "create_flow", "create_sequence", "create_favorite",
    "get_all_poses", "get_all_flows", "get_all_sequences", "get_all_favorites",
    "update_pose", "delete_pose", "create_practice_session",
    
    # Validation
    "validate_pose_name", "validate_duration", "validate_difficulty", "validate_new_pose_data",
    "validate_new_flow_data", "validate_database_integrity",
    
    # UI utilities
    "show_error_message", "show_success_message", "confirm_action", "hide_widgets", "show_widgets",
    
    # Image handling
    "load_pose_image", "load_thumbnail_image", "load_preview_image", "scale_image_for_display",
    
    # Display formatting
    "format_for_display", "format_for_internal", "format_list_for_display",
    "format_duration_display", "format_difficulty_display",
    
    # Date/time utilities  
    "get_current_timestamp", "format_practice_duration", "format_timer_display",
    
    # Sequence generation
    "select_flows_for_sequence", "get_available_styles", "calculate_section_durations",
    
    # System utilities
    "get_all_data", "validate_all_data", "cleanup_all_caches", "get_system_stats"
]