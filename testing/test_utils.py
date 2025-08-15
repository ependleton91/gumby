import pytest
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timedelta

# Add parent directory to Python path BEFORE any other imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now we can import PyQt6
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox

# Ensure QApplication exists for PyQt6 tests
app = QApplication.instance()
if app is None:
    app = QApplication([])

# Import only the functions that actually exist
from utils.file_utils import (
    safe_load_json, safe_save_json, ensure_directory_exists,
    create_backup_file, load_flows_data, load_poses_data
)
from utils.image_utils import (
    standardize_pose_name_to_filename, create_placeholder_image,
    validate_image_file, scale_image_for_display
)
from utils.validation_utils import (
    validate_pose_name, validate_duration, validate_difficulty,
    validate_muscle_groups, validate_sequence_name, validate_yoga_style
)
from utils.ui_utils import (
    hide_widgets, show_widgets, confirm_action, 
    show_error_message, center_widget_on_screen
)
from utils.datetime_utils import (
    format_duration_minutes, format_duration_seconds, parse_timestamp,
    format_time_ago, format_timer_display, parse_duration_input,
    get_current_timestamp
)
from utils.display_utils import (
    format_for_display, format_for_internal,
    format_list_for_display, format_list_for_internal
)
from utils.sequence_utils import (
    extract_unique_values, filter_flows_by_criteria,
    calculate_flow_compatibility_score, group_flows_by_category,
    calculate_total_sequence_duration
)


class TestFileUtils:
    """Test file operation utilities."""
    
    def test_safe_load_json_existing_file(self):
        """Test loading an existing JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {"test": "value", "number": 42}
            json.dump(test_data, f)
            temp_path = f.name
        
        result = safe_load_json(temp_path, {})
        assert result == test_data
        
        # Cleanup
        Path(temp_path).unlink()
    
    def test_safe_load_json_missing_file(self):
        """Test loading a non-existent file returns default."""
        default = {"default": "data"}
        result = safe_load_json("nonexistent.json", default)
        assert result == default
    
    def test_safe_load_json_corrupted_file(self):
        """Test loading corrupted JSON returns default."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_path = f.name
        
        default = {"default": "data"}
        result = safe_load_json(temp_path, default)
        assert result == default
        
        # Cleanup
        Path(temp_path).unlink()
    
    def test_safe_save_json(self):
        """Test saving JSON data."""
        test_data = {"flows": {"test_flow": {"name": "Test"}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        # Remove the temp file so we can test creation
        Path(temp_path).unlink()
        
        success = safe_save_json(temp_path, test_data)
        assert success
        
        # Verify content
        loaded_data = safe_load_json(temp_path, {})
        assert loaded_data == test_data
        
        # Cleanup
        Path(temp_path).unlink()
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "new_dir" / "test_file.json"
            ensure_directory_exists(test_path)
            assert test_path.parent.exists()


class TestImageUtils:
    """Test image handling utilities."""
    
    def test_standardize_pose_name_to_filename(self):
        """Test pose name to filename conversion."""
        assert standardize_pose_name_to_filename("Mountain Pose") == "mountain_pose.png"
        assert standardize_pose_name_to_filename("Child's Pose") == "childs_pose.png"
        assert standardize_pose_name_to_filename("Warrior I") == "warrior_i.png"
        assert standardize_pose_name_to_filename("Side Angle") == "side_angle.png"
        assert standardize_pose_name_to_filename("") == "no_image.png"
    
    def test_create_placeholder_image(self):
        """Test placeholder image creation."""
        pixmap = create_placeholder_image("Test Pose", 100, 100)
        assert not pixmap.isNull()
        assert pixmap.width() == 100
        assert pixmap.height() == 100
    
    def test_validate_image_file(self):
        """Test image file validation."""
        # Test with non-existent file
        assert not validate_image_file("nonexistent.png")
        
        # Test with invalid extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
        assert not validate_image_file(temp_path)
        Path(temp_path).unlink()


class TestValidationUtils:
    """Test data validation utilities."""
    
    def test_validate_pose_name_valid(self):
        """Test valid pose name validation."""
        valid, error, name = validate_pose_name("Mountain Pose")
        assert valid
        assert error == ""
        assert name == "Mountain Pose"
    
    def test_validate_pose_name_empty(self):
        """Test empty pose name validation."""
        valid, error, name = validate_pose_name("")
        assert not valid
        assert "cannot be empty" in error
    
    def test_validate_pose_name_too_short(self):
        """Test too short pose name."""
        valid, error, name = validate_pose_name("A")
        assert not valid
        assert "at least 2 characters" in error
    
    def test_validate_pose_name_invalid_characters(self):
        """Test invalid characters in pose name."""
        valid, error, name = validate_pose_name("Pose@#$")
        assert not valid
        assert "invalid characters" in error
    
    def test_validate_duration_valid(self):
        """Test valid duration validation."""
        valid, error, duration = validate_duration("5.5")
        assert valid
        assert error == ""
        assert duration == 5.5
    
    def test_validate_duration_invalid(self):
        """Test invalid duration validation."""
        valid, error, duration = validate_duration("not_a_number")
        assert not valid
        assert "valid number" in error
        assert duration == 0.0
    
    def test_validate_duration_negative(self):
        """Test negative duration."""
        valid, error, duration = validate_duration("-5")
        assert not valid
        assert "greater than 0" in error
    
    def test_validate_difficulty_valid(self):
        """Test valid difficulty validation."""
        valid, error, difficulty = validate_difficulty("3")
        assert valid
        assert error == ""
        assert difficulty == 3
    
    def test_validate_difficulty_out_of_range(self):
        """Test difficulty out of range."""
        valid, error, difficulty = validate_difficulty("10")
        assert not valid
        assert "between 1 and 5" in error
    
    def test_validate_muscle_groups_valid(self):
        """Test valid muscle groups."""
        valid, error, muscles = validate_muscle_groups(["core", "arms"])
        assert valid
        assert error == ""
        assert "core" in muscles
        assert "arms" in muscles
    
    def test_validate_muscle_groups_empty(self):
        """Test empty muscle groups."""
        valid, error, muscles = validate_muscle_groups([])
        assert not valid
        assert "at least one" in error
    
    def test_validate_sequence_name_valid(self):
        """Test valid sequence name."""
        valid, error = validate_sequence_name("Morning Flow")
        assert valid
        assert error == ""
    
    def test_validate_sequence_name_too_short(self):
        """Test too short sequence name."""
        valid, error = validate_sequence_name("AB")
        assert not valid
        assert "at least 3 characters" in error
    
    def test_validate_yoga_style_valid(self):
        """Test valid yoga style."""
        valid, error = validate_yoga_style("vinyasa")
        assert valid
        assert error == ""
    
    def test_validate_yoga_style_invalid(self):
        """Test invalid yoga style."""
        valid, error = validate_yoga_style("invalid_style")
        assert not valid
        assert "Invalid yoga style" in error


class TestUIUtils:
    """Test UI utility functions."""
    
    def test_hide_widgets(self):
        """Test hiding widgets."""
        widget1 = QWidget()
        widget2 = QWidget()
        
        widget1.setVisible(True)
        widget2.setVisible(True)
        
        hide_widgets([widget1, widget2])
        
        assert not widget1.isVisible()
        assert not widget2.isVisible()
    
    def test_show_widgets(self):
        """Test showing widgets."""
        widget1 = QWidget()
        widget2 = QWidget()
        
        widget1.setVisible(False)
        widget2.setVisible(False)
        
        show_widgets([widget1, widget2])
        
        assert widget1.isVisible()
        assert widget2.isVisible()
    
    def test_hide_widgets_with_none(self):
        """Test hiding widgets with None values."""
        widget1 = QWidget()
        widget1.setVisible(True)
        
        # Should not crash with None values
        hide_widgets([widget1, None])
        assert not widget1.isVisible()


class TestDateTimeUtils:
    """Test date and time utilities."""
    
    def test_format_duration_minutes(self):
        """Test duration formatting from minutes."""
        assert format_duration_minutes(1.5) == "1m 30s"
        assert format_duration_minutes(90) == "1h 30m"
        assert format_duration_minutes(0.5) == "30s"
        assert format_duration_minutes(60) == "1h"
        assert format_duration_minutes(5) == "5m"
        assert format_duration_minutes(0) == "0s"
    
    def test_format_duration_seconds(self):
        """Test duration formatting from seconds."""
        assert format_duration_seconds(90) == "1m 30s"
        assert format_duration_seconds(3665) == "1h 1m 5s"
        assert format_duration_seconds(45) == "45s"
        assert format_duration_seconds(0) == "0s"
    
    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        dt = parse_timestamp("2024-03-15 14:30:45")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 3
        assert dt.day == 15
        
        # Test invalid timestamp
        assert parse_timestamp("invalid") is None
        assert parse_timestamp("") is None
    
    def test_format_timer_display(self):
        """Test timer display formatting."""
        assert format_timer_display(125) == "02:05"
        assert format_timer_display(3665) == "1:01:05"
        assert format_timer_display(45) == "00:45"
        assert format_timer_display(0) == "00:00"
    
    def test_parse_duration_input(self):
        """Test duration input parsing."""
        assert parse_duration_input("1h 30m") == 90.0
        assert parse_duration_input("45") == 45.0
        assert parse_duration_input("1.5h") == 90.0
        assert parse_duration_input("30m") == 30.0
        assert parse_duration_input("invalid") is None
        assert parse_duration_input("") is None
    
    def test_get_current_timestamp(self):
        """Test current timestamp generation."""
        timestamp = get_current_timestamp()
        assert len(timestamp) == 19  # "YYYY-MM-DD HH:MM:SS"
        assert timestamp[4] == "-"
        assert timestamp[7] == "-"
        assert timestamp[10] == " "


class TestDisplayUtils:
    """Test display formatting utilities."""
    
    def test_format_for_display(self):
        """Test formatting internal text for display."""
        assert format_for_display("full_body") == "Full Body"
        assert format_for_display("pelvic_floor") == "Pelvic Floor"
        assert format_for_display("vinyasa") == "Vinyasa"
        assert format_for_display("hip_flexors") == "Hip Flexors"
        assert format_for_display("") == ""
    
    def test_format_for_internal(self):
        """Test formatting display text for internal use."""
        assert format_for_internal("Full Body") == "full_body"
        assert format_for_internal("Pelvic Floor") == "pelvic_floor"
        assert format_for_internal("Vinyasa") == "vinyasa"
        assert format_for_internal("Hip Flexors") == "hip_flexors"
        assert format_for_internal("") == ""
    
    def test_format_list_for_display(self):
        """Test formatting lists for display."""
        internal_list = ["core", "full_body", "pelvic_floor"]
        display_list = format_list_for_display(internal_list)
        assert display_list == ["Core", "Full Body", "Pelvic Floor"]
    
    def test_format_list_for_internal(self):
        """Test formatting display lists for internal use."""
        display_list = ["Core", "Full Body", "Pelvic Floor"]
        internal_list = format_list_for_internal(display_list)
        assert internal_list == ["core", "full_body", "pelvic_floor"]


class TestSequenceUtils:
    """Test sequence building utilities."""
    
    def test_extract_unique_values(self):
        """Test extracting unique values from flows data."""
        flows_data = {
            "flowing_sequences": {
                "flow1": {"style": ["vinyasa", "hatha"], "difficulty": 2},
                "flow2": {"style": ["yin"], "difficulty": 1},
                "flow3": {"style": ["vinyasa"], "difficulty": 3}
            }
        }
        
        styles = extract_unique_values(flows_data, "style")
        assert set(styles) == {"hatha", "vinyasa", "yin"}
        assert styles == sorted(styles)  # Should be sorted
    
    def test_filter_flows_by_criteria(self):
        """Test filtering flows by criteria."""
        flows = [
            {"style": ["vinyasa"], "difficulty": 2, "muscle_groups": ["core"]},
            {"style": ["hatha"], "difficulty": 1, "muscle_groups": ["arms"]},
            {"style": ["vinyasa"], "difficulty": 3, "muscle_groups": ["core", "arms"]}
        ]
        
        criteria = {"style": ["vinyasa"], "difficulty_max": 2}
        filtered = filter_flows_by_criteria(flows, criteria)
        
        assert len(filtered) == 1
        assert filtered[0]["difficulty"] == 2
    
    def test_calculate_flow_compatibility_score(self):
        """Test flow compatibility scoring."""
        flow = {
            "muscle_groups": ["core", "arms"],
            "energy_level": "building",
            "difficulty": 2,
            "duration": 5
        }
        
        criteria = {
            "target_muscles": ["core"],
            "preferred_energy": "building",
            "target_difficulty": 2,
            "target_duration": 5
        }
        
        score = calculate_flow_compatibility_score(flow, criteria)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be a good match
    
    def test_group_flows_by_category(self):
        """Test grouping flows by category."""
        flows = [
            {"category": "warm_up", "name": "Sun Salutation"},
            {"category": "main_flow", "name": "Warrior Flow"},
            {"category": "warm_up", "name": "Gentle Warmup"},
            {"category": "cool_down", "name": "Relaxation"}
        ]
        
        grouped = group_flows_by_category(flows)
        
        assert len(grouped["warm_up"]) == 2
        assert len(grouped["main_flow"]) == 1
        assert len(grouped["cool_down"]) == 1
    
    def test_calculate_total_sequence_duration(self):
        """Test calculating total sequence duration."""
        flows = [
            {"duration": 5.0},
            {"duration": 10.5},
            {"duration": 2.25}
        ]
        
        total = calculate_total_sequence_duration(flows)
        assert total == 17.75


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main(["-v", __file__])