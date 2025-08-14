# Import commonly used functions for easy access

from .file_utils import (
    safe_load_json, safe_save_json, 
    load_flows_data, load_poses_data, load_favorites_data,
    save_flows_data, save_poses_data, save_favorites_data,
    ensure_directory_exists, create_backup_file, list_backup_files
)

from .image_utils import (
    load_pose_image, scale_image_for_display, standardize_pose_name_to_filename,
    load_thumbnail_image, load_preview_image, load_carousel_image,
    clear_image_cache, get_cache_stats, create_placeholder_image,
    validate_image_file, get_image_info, load_image_from_path
)

from .validation_utils import (
    validate_pose_name, validate_duration, validate_difficulty,
    validate_muscle_groups, validate_sequence_name, validate_yoga_style,
    validate_sequence_data, validate_email, validate_rating,
    validate_practice_notes, sanitize_filename,
    validate_new_pose_data, validate_new_sequence_data
)

from .ui_utils import (
    hide_widgets, show_widgets, enable_widgets, disable_widgets,
    show_error_message, show_warning_message, show_info_message, 
    show_success_message, confirm_action, confirm_destructive_action,
    center_widget_on_screen, center_widget_on_parent, set_widget_loading_state,
    toggle_widget_visibility, clear_layout, create_separator_line,
    show_pose_validation_errors, confirm_sequence_delete, confirm_pose_delete,
    show_save_success, create_button_with_icon, ProgressDialog
)

from .datetime_utils import (
    get_current_timestamp, get_current_date, get_current_time,
    format_duration_minutes, format_duration_seconds, format_practice_duration,
    parse_timestamp, calculate_session_duration, format_time_ago,
    format_timer_display, parse_duration_input, is_recent_timestamp,
    get_practice_session_summary, get_practice_date_display, get_sequence_age_display
)

from .display_utils import (
    format_for_display, format_for_internal,
    format_list_for_display, format_list_for_internal,
    format_muscle_groups_display, format_style_list_display
)

from .sequence_utils import (
    extract_unique_values, filter_flows_by_criteria,
    calculate_flow_compatibility_score, select_best_flows_for_time,
    load_class_template, get_available_styles, calculate_section_durations,
    group_flows_by_category, select_flows_for_sequence,
    validate_sequence_structure, optimize_sequence_order,
    get_flow_summary, calculate_total_sequence_duration, get_sequence_muscle_groups
)

# Define what gets imported with "from utils import *"
__all__ = [
    # File operations
    'safe_load_json', 'safe_save_json',
    'load_flows_data', 'load_poses_data', 'load_favorites_data',
    'save_flows_data', 'save_poses_data', 'save_favorites_data',
    'ensure_directory_exists', 'create_backup_file', 'list_backup_files',
    
    # Image operations  
    'load_pose_image', 'scale_image_for_display', 'standardize_pose_name_to_filename',
    'load_thumbnail_image', 'load_preview_image', 'load_carousel_image', 
    'clear_image_cache', 'get_cache_stats', 'create_placeholder_image',
    'validate_image_file', 'get_image_info', 'load_image_from_path',
    
    # Validation
    'validate_pose_name', 'validate_duration', 'validate_difficulty',
    'validate_muscle_groups', 'validate_sequence_name', 'validate_yoga_style',
    'validate_sequence_data', 'validate_email', 'validate_rating',
    'validate_practice_notes', 'sanitize_filename',
    'validate_new_pose_data', 'validate_new_sequence_data',
    
    # UI helpers
    'hide_widgets', 'show_widgets', 'enable_widgets', 'disable_widgets',
    'show_error_message', 'show_warning_message', 'show_info_message', 'show_success_message',
    'confirm_action', 'confirm_destructive_action', 'center_widget_on_screen', 'center_widget_on_parent',
    'set_widget_loading_state', 'toggle_widget_visibility', 'clear_layout', 'create_separator_line',
    'show_pose_validation_errors', 'confirm_sequence_delete', 'confirm_pose_delete',
    'show_save_success', 'create_button_with_icon', 'ProgressDialog',
    
    # Date/time
    'get_current_timestamp', 'get_current_date', 'get_current_time',
    'format_duration_minutes', 'format_duration_seconds', 'format_practice_duration',
    'parse_timestamp', 'calculate_session_duration', 'format_time_ago',
    'format_timer_display', 'parse_duration_input', 'is_recent_timestamp',
    'get_practice_session_summary', 'get_practice_date_display', 'get_sequence_age_display',
    
    # Display formatting
    'format_for_display', 'format_for_internal',
    'format_list_for_display', 'format_list_for_internal',
    'format_muscle_groups_display', 'format_style_list_display',
    
    # Sequence utilities
    'extract_unique_values', 'filter_flows_by_criteria',
    'calculate_flow_compatibility_score', 'select_best_flows_for_time',
    'load_class_template', 'get_available_styles', 'calculate_section_durations',
    'group_flows_by_category', 'select_flows_for_sequence',
    'validate_sequence_structure', 'optimize_sequence_order',
    'get_flow_summary', 'calculate_total_sequence_duration', 'get_sequence_muscle_groups'
]

# Package metadata
__version__ = "1.0.0"
__author__ = "GUMBY Development Team"
__description__ = "Utility functions for GUMBY yoga sequence generator"