# Import commonly used functions for easy access

from .file_utils import (
    safe_load_json, safe_save_json, 
    load_flows_data, load_poses_data, load_favorites_data,
    save_flows_data, save_poses_data, save_favorites_data
)

from .image_utils import (
    load_pose_image, scale_image_for_display, standardize_pose_name_to_filename,
    load_thumbnail_image, load_preview_image, load_carousel_image,
    clear_image_cache
)

from .validation_utils import (
    validate_pose_name, validate_duration, validate_difficulty,
    validate_muscle_groups, validate_sequence_name
)

from .ui_utils import (
    hide_widgets, show_widgets, enable_widgets, disable_widgets,
    show_error_message, show_warning_message, show_info_message, 
    show_success_message, confirm_action, confirm_destructive_action,
    center_widget_on_screen, set_widget_loading_state,
    show_pose_validation_errors, confirm_sequence_delete, confirm_pose_delete
)

from .datetime_utils import (
    get_current_timestamp, get_current_date, format_duration_minutes,
    format_duration_seconds, format_practice_duration, format_time_ago,
    format_timer_display, parse_duration_input
)

# Define what gets imported with "from utils import *"
__all__ = [
    # File operations
    'safe_load_json', 'safe_save_json',
    'load_flows_data', 'load_poses_data', 'load_favorites_data',
    'save_flows_data', 'save_poses_data', 'save_favorites_data',
    
    # Image operations  
    'load_pose_image', 'scale_image_for_display', 'standardize_pose_name_to_filename',
    'load_thumbnail_image', 'load_preview_image', 'load_carousel_image', 'clear_image_cache',
    
    # Validation
    'validate_pose_name', 'validate_duration', 'validate_difficulty',
    'validate_muscle_groups', 'validate_sequence_name', 'validate_rating',
    'validate_new_pose_data',
    
    # UI helpers
    'hide_widgets', 'show_widgets', 'enable_widgets', 'disable_widgets',
    'show_error_message', 'show_warning_message', 'show_info_message', 'show_success_message',
    'confirm_action', 'confirm_destructive_action', 'center_widget_on_screen',
    'set_widget_loading_state', 'show_pose_validation_errors', 
    'confirm_sequence_delete', 'confirm_pose_delete',
    
    # Date/time
    'get_current_timestamp', 'get_current_date', 'format_duration_minutes',
    'format_duration_seconds', 'format_practice_duration', 'format_time_ago',
    'format_timer_display', 'parse_duration_input'
]

# Package metadata
__version__ = "1.0.0"
__author__ = "GUMBY Development Team"
__description__ = "Utility functions for GUMBY yoga sequence generator"