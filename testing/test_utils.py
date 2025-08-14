import pytest
import tempfile
from pathlib import Path
from utils.file_utils import safe_load_json
from utils.image_utils import standardize_pose_name_to_filename, create_placeholder_image
from utils.validation_utils import validate_pose_name, validate_duration
from utils.ui_utils import confirm_action
from utils.datetime_utils import format_duration_minutes, parse_duration_input
import sys
from PySide6.QtWidgets import QApplication

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

class TestFileUtils:
    def test_safe_load_json_existing_file(self):
        """Test loading an existing JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {"test": "value"}
            import json
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

class TestImageUtils:
    def test_standardize_pose_name_to_filename(self):
        """Test pose name to filename conversion."""
        assert standardize_pose_name_to_filename("Mountain Pose") == "mountain_pose.png"
        assert standardize_pose_name_to_filename("Child's Pose") == "childs_pose.png"
        assert standardize_pose_name_to_filename("Warrior I") == "warrior_i.png"
    
    def test_create_placeholder_image(self):
        """Test placeholder image creation."""
        pixmap = create_placeholder_image("Test Pose", 100, 100)
        assert not pixmap.isNull()
        assert pixmap.width() == 100
        assert pixmap.height() == 100

class TestValidationUtils:
    def test_validate_pose_name_valid(self):
        """Test valid pose name validation."""
        valid, error = validate_pose_name("Mountain Pose")
        assert valid
        assert error == ""
    
    def test_validate_pose_name_empty(self):
        """Test empty pose name validation."""
        valid, error = validate_pose_name("")
        assert not valid
        assert "cannot be empty" in error
    
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

class TestDateTimeUtils:
    def test_format_duration_minutes(self):
        """Test duration formatting."""
        assert format_duration_minutes(1.5) == "1m 30s"
        assert format_duration_minutes(90) == "1h 30m"
        assert format_duration_minutes(0.5) == "30s"
    
    def test_parse_duration_input(self):
        """Test duration input parsing."""
        assert parse_duration_input("1h 30m") == 90.0
        assert parse_duration_input("45") == 45.0
        assert parse_duration_input("1.5h") == 90.0
        assert parse_duration_input("invalid") is None