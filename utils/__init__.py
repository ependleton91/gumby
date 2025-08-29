# Import functions that work with database-first approach

from .file_utils import (
    ensure_directory_exists,
    load_flows_data, load_poses_data, load_favorites_data,
    save_flows_data, save_poses_data, save_favorites_data,  # Kept for compatibility
    update_favorites_after_pose_change, remove_pose_from_favorites,
    export_database_to_json
)

from .image_utils import (
    ImageCache,
    standardize_pose_name_to_filename, load_pose_image, load_image_from_path,
    scale_image_for_display, create_placeholder_image, validate_image_file, 
    clear_image_cache, load_thumbnail_image, load_preview_image
)

from .validation_utils import (
    validate_pose_name, validate_duration, validate_difficulty,
    validate_muscle_groups, validate_sequence_name, validate_yoga_style,
    validate_sequence_data, validate_new_pose_data,
    validate_pose_name_unique, validate_flow_name_unique,
    validate_database_integrity, cleanup_broken_favorites
)

from .ui_utils import (
    hide_widgets, show_widgets, enable_widgets, disable_widgets,
    toggle_widget_visibility, clear_layout,
    show_error_message, show_warning_message, show_info_message, 
    show_success_message, confirm_action, confirm_destructive_action,
    center_widget_on_screen, set_widget_loading_state, create_separator_line,
    show_pose_validation_errors, confirm_sequence_delete, confirm_pose_delete,
    show_save_success
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

# Import database utilities for direct use
from .database_utils import (
    get_db_manager, create_pose, create_flow, create_favorite,
    get_all_poses, get_all_flows, get_all_favorites,
    update_pose, delete_pose
)