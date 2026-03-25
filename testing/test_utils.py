import pytest
import tempfile
import sys
from pathlib import Path
import logging
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

from utils.file_utils import (
    ensure_directory_exists,load_flows_data, load_poses_data, 
    load_favorite_flows,load_favorite_poses, load_favorite_sequences,
    remove_flow_from_favorites,remove_pose_from_favorites,
    remove_sequence_from_favorites
)
from utils.database_utils import (
    get_db_manager,ensure_muscle_group_exists, ensure_yoga_style_exists,
    get_pose_by_name,get_flow_by_name,get_style_by_name,create_pose,
    get_all_poses,update_pose,delete_pose,create_flow,get_all_flows,update_flow,
    delete_flow,create_sequence,get_all_sequences,create_favorite,get_favorite_poses,
    get_favorite_flows,get_favorite_sequences,delete_favorite,create_practice_session,
    get_practice_sessions,get_all_muscle_groups,get_all_yoga_styles,get_sequence_with_full_flows,
    get_flow_with_full_poses
)
from utils.image_utils import (
    standardize_pose_name_to_filename, create_placeholder_image,
    validate_image_file
)
from utils.validation_utils import (
    validate_pose_name, validate_duration, validate_difficulty,
    validate_muscle_groups, validate_sequence_name, validate_yoga_style
)
from utils.ui_utils import (
    hide_widgets, show_widgets
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
    load_class_template,get_available_styles,filter_flows_by_criteria,
    calculate_flow_compatibility_score, select_best_flows_for_time, 
    calculate_section_durations, group_flows_by_category, select_flows_for_sequence,
    validate_sequence_structure,optimize_sequence_order, get_flow_summary, calculate_total_sequence_duration,
    get_sequence_muscle_groups
)

#UPDATED 3/24/26
class TestDatabaseUtils:
    def get_db_manager(self):
        logging.info("Testing database manager retrieval")
        test = get_db_manager()
        logging.info(f"Database manager instance: {test}")

    def ensure_muscle_group_exists(self):
        logging.info("Testing ensuring muscle group exists: arms, expecting success")
        ensure_muscle_group_exists("arms")
        logging.info("Testing ensuring muscle group exists: invalid_muscle, expecting failure")
        ensure_muscle_group_exists("invalid_muscle")

    def ensure_yoga_style_exists(self):
        logging.info("Testing ensuring yoga style exists: hatha, expecting success")
        ensure_yoga_style_exists("hatha")
        logging.info("Testing ensuring yoga style exists: invalid_style, expecting failure")
        ensure_yoga_style_exists("invalid_style")

    def get_pose_by_name(self):
        logging.info("Testing get pose by name: Mountain Pose, expecting success")
        successTest = get_pose_by_name("Mountain Pose")
        logging.info(f"Get pose by name success: {successTest}")

        logging.info("Testing get pose by name: Invalid Pose, expecting failure")
        failureTest = get_pose_by_name("Invalid Pose")
        logging.info(f"Get pose by name failure: {failureTest}")

    def get_flow_by_name(self):
        logging.info("Testing get flow by name: Sun Salutation Flow, expecting success")
        successTest = get_flow_by_name("Sun Salutation Flow")
        logging.info(f"Get flow by name success: {successTest}")

        logging.info("Testing get flow by name: Invalid Flow, expecting failure")
        failureTest = get_flow_by_name("Invalid Flow")
        logging.info(f"Get flow by name failure: {failureTest}")

    def get_style_by_name(self):
        logging.info("Testing get style by name: hatha, expecting success")
        successTest = get_style_by_name("hatha")
        logging.info(f"Get style by name success: {successTest}")

        logging.info("Testing get style by name: Invalid Style, expecting failure")
        failureTest = get_style_by_name("Invalid Style")
        logging.info(f"Get style by name failure: {failureTest}")

    def create_pose(self):
        logging.info("Testing create pose")
        pose_data = {
            "name": "Test Pose",
            "default_duration": 30,
            "type": "standing",
            "difficulty": "easy",
            "description": "A test pose",
            "instructions": "Stand tall and breathe",
            "modifications": "Use a chair for support",
            "image_filename": "test_pose.png"
        }
        successTest = create_pose(pose_data)
        logging.info(f"Create pose success: {successTest}")

    def get_all_poses(self):
        logging.info("Testing get all poses")
        test = get_all_poses()
        logging.info(f"Get all poses success: {test}")

    def update_pose(self):
        logging.info("Testing update pose")
        pose_data = {
            "name": "Updated Test Pose",
            "default_duration": 45,
            "type": "seated",
            "difficulty": "medium",
            "description": "An updated test pose",
            "instructions": "Sit tall and breathe deeply",
            "modifications": "Use a cushion for support",
            "image_filename": "updated_test_pose.png"
        }
        successTest = update_pose("Test Pose", pose_data)
        logging.info(f"Update pose success: {successTest}")

    def delete_pose(self):
        logging.info("Testing delete pose")
        successTest = delete_pose("Updated Test Pose")
        logging.info(f"Delete pose success: {successTest}")

    def create_flow(self):
        logging.info("Testing create flow")
        test_flow = {
            "name": "Test Flow",
            "duration": 60,
            "category": "Vinyasa",
            "difficulty": 2,
            "energy_level": 3
        }
        successTest = create_flow(test_flow)
        logging.info(f"Create flow success: {successTest}")

    def get_all_flows(self):
        logging.info("Testing get all flows")
        test = get_all_flows()
        logging.info(f"Get all flows success: {test}")

    def update_flow(self):
        logging.info("Testing update flow")
        flow_data = {
            "name": "Updated Test Flow",
            "duration": 75,
            "category": "Vinyasa",
            "difficulty": 3,
            "energy_level": 4
        }
        successTest = update_flow("Test Flow", flow_data)
        logging.info(f"Update flow success: {successTest}")

    def delete_flow(self):
        logging.info("Testing delete flow")
        successTest = delete_flow("Updated Test Flow")
        logging.info(f"Delete flow success: {successTest}")

    def create_sequence(self):
        logging.info("Testing create sequence")
        flows_data = {
            "Test Flow": {
                "duration": 60,
                "category": "Vinyasa",
                "difficulty": 2,
                "energy_level": 3
            }
        }
        sequence_data = {
            "name": "Test Sequence",
            "duration": 0,
            "flows_data": flows_data,
            "style": "Vinyasa",
            "muscle_groups": ["hamstrings", "quadriceps"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        success_test = create_sequence(sequence_data)
        logging.info(f"Create sequence success: {success_test}")


    def get_all_sequences(self):
        logging.info("Testing get all sequences")
        test = get_all_sequences()
        logging.info(f"Get all sequences success: {test}")

    def create_favorite(self):
        logging.info("Testing create favorite - pose")
        success_test = create_favorite("Upward Salute", "pose", 2)
        logging.info(f"Create favorite pose success: {success_test}")

        logging.info("Testing create favorite - flow")
        success_test = create_favorite("Warrior Standing Flow", "flow", 2)
        logging.info(f"Create favorite flow success: {success_test}")

        logging.info("Testing create favorite - sequence")
        success_test = create_favorite("Hatha 64 Minute Flow", "sequence", 111111)
        logging.info(f"Create favorite sequence success: {success_test}")

    def get_favorite_poses(self):
        logging.info("Testing get favorite poses")
        test = get_favorite_poses()
        logging.info(f"Get favorite poses success: {test}")

    def get_favorite_flows(self):
        logging.info("Testing get favorite flows")
        test = get_favorite_flows()
        logging.info(f"Get favorite flows success: {test}")

    def get_favorite_sequences(self):
        logging.info("Testing get favorite sequences")
        test = get_favorite_sequences()
        logging.info(f"Get favorite sequences success: {test}")

    def delete_favorite(self):
        favorite_info = get_favorite_poses()
        for favorites in favorite_info:
            if favorites["name"] == "Upward Salute":
                logging.info("Testing delete favorite")
                success_test = delete_favorite(favorites["id"])
                logging.info(f"Delete favorite success: {success_test}")
                if success_test:
                    logging.info("Favorite deleted successfully")
                    logging.info("Re-creating favorite for future tests")
                    create_favorite("Upward Salute", "pose", 2)
                else:
                    logging.warning("Failed to delete favorite")

    def create_practice_session(self):
        logging.info("Testing create practice session")
        test_session = {
                "session_date": datetime.now(),
                "sequence_name": "Test Sequence",
                "duration_minutes": 60,
                "rating": 3,
                "notes": "A great practice session!",
                "sequence_data": ""
            }
        create_practice_session(test_session)

    def get_practice_sessions(self):
        logging.info("Testing get practice sessions")
        test = get_practice_sessions()
        logging.info(f"Get practice sessions success: {test}")

    def get_all_muscle_groups(self):
        logging.info("Testing get all muscle groups")
        test = get_all_muscle_groups()
        logging.info(f"Get all muscle groups success: {test}")

    def get_all_yoga_styles(self):
        logging.info("Testing get all yoga styles")
        test = get_all_yoga_styles()
        logging.info(f"Get all yoga styles success: {test}")

    def get_sequence_with_full_flows(self):
        logging.info("Testing get sequence with full flows")
        sequences = get_all_sequences()
        test = get_sequence_with_full_flows(sequences[1]["id"])
        logging.info(f"Get sequence with full flows success: {test}")

    def get_flow_with_full_poses(self):
        logging.info("Testing get flow with full poses")

#UPDATED 3/24/26
class TestFileUtils:

    def test_ensure_directory_exists(self):
        logging
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "new_dir" / "test_file.json"
            ensure_directory_exists(test_path)
            assert test_path.parent.exists()

    def load_favorite_flows(self):
        logging.info("Testing loading of favorite flows")
        favorite_flows = load_favorite_flows()
        logging.info(f"Loaded favorite flows: {favorite_flows}")

    def load_favorite_poses(self):
        logging.info("Testing loading of favorite poses")
        favorite_poses = load_favorite_poses()
        logging.info(f"Loaded favorite poses: {favorite_poses}")

    def load_favorite_sequences(self):
        logging.info("Testing loading of favorite sequences")
        favorite_sequences = load_favorite_sequences()
        logging.info(f"Loaded favorite sequences: {favorite_sequences}")

    def remove_flow_from_favorites(self):
        logging.info("Testing removal of flow from favorites")
        remove_flow_from_favorites("Test Flow")

    def remove_pose_from_favorites(self):
        logging.info("Testing removal of pose from favorites")
        remove_pose_from_favorites("Test Pose")

    def remove_sequence_from_favorites(self):
        logging.info("Testing removal of sequence from favorites")
        remove_sequence_from_favorites("Test Sequence")



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
        assert "At least one" in error
    
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