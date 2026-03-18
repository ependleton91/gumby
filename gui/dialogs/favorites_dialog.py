from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QTextEdit, QPushButton, QFormLayout, QLabel, 
    QComboBox, QVBoxLayout, QHBoxLayout, QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt
from utils.ui_utils import show_error_message, show_pose_validation_errors
from utils.validation_utils import validate_sequence_name
from utils.database_utils import create_favorite
from utils.datetime_utils import get_current_timestamp
import logging

logger = logging.getLogger(__name__)


class favorites_dialog_box(QDialog):
    def __init__(self, sequence_data, sequence_type="sequence"):
        super().__init__()
        self.sequence_data = sequence_data
        self.sequence_type = sequence_type
        
        self.setWindowTitle("Save to Favorites")
        self.setFixedSize(500, 400)
        
        self.setup_ui()
        self.populate_defaults()
        self.setup_validation()

    def setup_ui(self):
        """Create the user interface elements."""
        main_layout = QVBoxLayout()
        
        # Form section
        form_layout = QFormLayout()
        
        # Name field
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Enter a name for this favorite...")
        
        # Description field
        self.description_field = QTextEdit()
        self.description_field.setMaximumHeight(80)
        self.description_field.setPlaceholderText("Optional description...")
        
        # Type selection
        self.type_field = QComboBox()
        self.type_field.addItems(["sequence", "flow", "pose"])
        self.type_field.setCurrentText(self.sequence_type)
        
        # Priority field (optional)
        self.priority_field = QSpinBox()
        self.priority_field.setRange(1, 5)
        self.priority_field.setValue(3)
        self.priority_field.setSuffix(" stars")
        
        # Validation feedback
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red; font-size: 10px;")
        self.validation_label.setVisible(False)
        
        # Add fields to form
        form_layout.addRow("Name:", self.name_field)
        form_layout.addRow("Description:", self.description_field)
        form_layout.addRow("Type:", self.type_field)
        form_layout.addRow("Priority:", self.priority_field)
        form_layout.addRow("", self.validation_label)
        
        # Summary section
        summary_group = self.create_summary_section()
        
        # Button section
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("SAVE TO FAVORITES")
        self.cancel_button = QPushButton("CANCEL")
        
        self.save_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px 20px; border-radius: 4px; font-weight: bold;")
        self.cancel_button.setStyleSheet("background-color: #6c757d; color: white; padding: 10px 20px; border-radius: 4px;")
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # Connect buttons
        self.save_button.clicked.connect(self.save_favorite)
        self.cancel_button.clicked.connect(self.reject)
        
        # Add to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(summary_group)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def create_summary_section(self):
        """Create summary section showing what will be saved."""
        group_box = QGroupBox("What You're Saving")
        layout = QVBoxLayout()
        
        summary_text = self.generate_summary_text()
        self.summary_label = QLabel(summary_text)
        self.summary_label.setStyleSheet("""
            font-family: monospace; 
            background-color: #f8f9fa; 
            border: 1px solid #dee2e6;
            border-radius: 4px; 
            padding: 10px;
            line-height: 1.4;
        """)
        self.summary_label.setWordWrap(True)
        
        layout.addWidget(self.summary_label)
        group_box.setLayout(layout)
        return group_box

    def generate_summary_text(self):
        """Generate summary text based on sequence data and type."""
        if self.sequence_type == "sequence":
            return self.generate_sequence_summary()
        elif self.sequence_type == "flow":
            return self.generate_flow_summary()
        elif self.sequence_type == "pose":
            return self.generate_pose_summary()
        else:
            return "Unknown item type"

    def generate_sequence_summary(self):
        """Generate summary for sequence favorite."""
        flows = self.sequence_data.get("flows", [])
        if not flows:
            return "Empty sequence"
        
        total_duration = sum(flow.get("duration", 0) for flow in flows)
        flow_count = len(flows)
        
        summary = f"Sequence Summary:\n"
        summary += f"• {flow_count} flows\n"
        summary += f"• Total duration: {total_duration:.1f} minutes\n"
        
        # Show muscle groups if available
        muscle_groups = self.sequence_data.get("muscle_groups", [])
        if muscle_groups:
            summary += f"• Target muscles: {', '.join(muscle_groups[:3])}"
            if len(muscle_groups) > 3:
                summary += f" and {len(muscle_groups) - 3} more"
            summary += "\n"
        
        # Show first few flow names
        summary += f"\nFlows included:\n"
        for i, flow in enumerate(flows[:5], 1):
            flow_name = flow.get("name", "Unknown Flow")
            flow_duration = flow.get("duration", 0)
            summary += f"{i}. {flow_name} ({flow_duration:.1f}min)\n"
        
        if len(flows) > 5:
            summary += f"... and {len(flows) - 5} more flows"
        
        return summary

    def generate_flow_summary(self):
        """Generate summary for flow favorite."""
        flow_name = self.sequence_data.get("name", "Unknown Flow")
        duration = self.sequence_data.get("duration", 0)
        difficulty = self.sequence_data.get("difficulty", 1)
        category = self.sequence_data.get("category", "Unknown")
        
        poses = self.sequence_data.get("flow", [])
        pose_count = len(poses)
        
        summary = f"Flow Summary:\n"
        summary += f"• Name: {flow_name}\n"
        summary += f"• Duration: {duration} minutes\n"
        summary += f"• Difficulty: {difficulty}/5\n"
        summary += f"• Category: {category}\n"
        summary += f"• Poses: {pose_count} poses\n"
        
        if poses:
            summary += f"\nPoses included:\n"
            for i, pose in enumerate(poses[:3], 1):
                pose_name = pose.get("name", "Unknown Pose")
                summary += f"{i}. {pose_name}\n"
            
            if len(poses) > 3:
                summary += f"... and {len(poses) - 3} more poses"
        
        return summary

    def generate_pose_summary(self):
        """Generate summary for pose favorite."""
        pose_name = self.sequence_data.get("name", "Unknown Pose")
        duration = self.sequence_data.get("default_duration", 0)
        difficulty = self.sequence_data.get("difficulty", 1)
        pose_type = self.sequence_data.get("type", "Unknown")
        
        muscle_groups = self.sequence_data.get("muscle_groups", [])
        
        summary = f"Pose Summary:\n"
        summary += f"• Name: {pose_name}\n"
        summary += f"• Duration: {duration} minutes\n"
        summary += f"• Difficulty: {difficulty}/5\n"
        summary += f"• Type: {pose_type}\n"
        
        if muscle_groups:
            summary += f"• Targets: {', '.join(muscle_groups)}\n"
        
        description = self.sequence_data.get("description", "")
        if description:
            summary += f"\nDescription: {description[:100]}"
            if len(description) > 100:
                summary += "..."
        
        return summary

    def populate_defaults(self):
        """Populate form with intelligent defaults."""
        # Generate default name based on content
        default_name = self.generate_default_name()
        self.name_field.setText(default_name)
        
        # Generate default description
        default_description = self.generate_default_description()
        self.description_field.setText(default_description)

    def generate_default_name(self):
        """Generate intelligent default name based on content."""
        if self.sequence_type == "sequence":
            flows = self.sequence_data.get("flows", [])
            total_duration = sum(flow.get("duration", 0) for flow in flows)
            styles = self.sequence_data.get("style", [])
            style_name = styles[0] if styles else "Mixed"
            return f"{style_name.title()} {int(total_duration)}min Sequence"
        
        elif self.sequence_type == "flow":
            flow_name = self.sequence_data.get("name", "Custom Flow")
            return f"Favorite: {flow_name}"
        
        elif self.sequence_type == "pose":
            pose_name = self.sequence_data.get("name", "Custom Pose")
            return f"Favorite: {pose_name}"
        
        return "My Favorite"

    def generate_default_description(self):
        """Generate default description based on content."""
        if self.sequence_type == "sequence":
            muscle_groups = self.sequence_data.get("muscle_groups", [])
            styles = self.sequence_data.get("style", [])
            
            desc = f"Generated sequence"
            if styles:
                desc += f" in {', '.join(styles)} style"
            if muscle_groups:
                desc += f" targeting {', '.join(muscle_groups[:3])}"
                if len(muscle_groups) > 3:
                    desc += f" and {len(muscle_groups) - 3} more muscle groups"
            
            return desc
        
        elif self.sequence_type == "flow":
            category = self.sequence_data.get("category", "")
            energy = self.sequence_data.get("energy_level", "")
            
            desc = f"Saved flow"
            if category:
                desc += f" from {category} category"
            if energy:
                desc += f" with {energy} energy"
            
            return desc
        
        elif self.sequence_type == "pose":
            muscle_groups = self.sequence_data.get("muscle_groups", [])
            desc = f"Saved pose"
            if muscle_groups:
                desc += f" targeting {', '.join(muscle_groups)}"
            return desc
        
        return "Saved from GUMBY yoga app"

    def setup_validation(self):
        """Setup real-time validation."""
        self.name_field.textChanged.connect(self.validate_name)

    def validate_name(self):
        """Validate favorite name and show feedback."""
        name = self.name_field.text().strip()
        
        if not name:
            self.show_validation_error("Name is required")
            return False
        
        # Validate name format
        valid, error = validate_sequence_name(name)
        if not valid:
            self.show_validation_error(error)
            return False
        
        # Check for duplicate favorite names
        try:
            existing = get_favorite_by_name(name)
            if existing:
                self.show_validation_error(f"Favorite named '{name}' already exists")
                return False
        except Exception as e:
            logger.warning(f"Could not check favorite name uniqueness: {e}")
        
        self.clear_validation_error()
        return True

    def show_validation_error(self, message):
        """Show validation error message."""
        self.validation_label.setText(message)
        self.validation_label.setVisible(True)
        self.save_button.setEnabled(False)

    def clear_validation_error(self):
        """Clear validation error display."""
        self.validation_label.setVisible(False)
        self.save_button.setEnabled(True)

    def get_favorite_data(self):
        """Extract favorite data for database storage."""
        base_data = {
            "name": self.name_field.text().strip(),
            "type": self.type_field.currentText(),
            "description": self.description_field.toPlainText().strip(),
            "priority": self.priority_field.value(),
            "created_at": get_current_timestamp()
        }
        
        # Add type-specific data
        if self.sequence_type == "sequence":
            base_data.update({
                "total_duration": sum(flow.get("duration", 0) for flow in self.sequence_data.get("flows", [])),
                "flow_count": len(self.sequence_data.get("flows", [])),
                "muscle_groups": self.sequence_data.get("muscle_groups", []),
                "style": self.sequence_data.get("style", []),
                "flows": self.sequence_data.get("flows", [])
            })
        
        elif self.sequence_type == "flow":
            base_data.update({
                "flow_data": self.sequence_data,
                "duration": self.sequence_data.get("duration", 0),
                "pose_count": len(self.sequence_data.get("flow", []))
            })
        
        elif self.sequence_type == "pose":
            base_data.update({
                "pose_data": self.sequence_data,
                "duration": self.sequence_data.get("default_duration", 0),
                "difficulty": self.sequence_data.get("difficulty", 1)
            })
        
        return base_data

    def save_favorite(self):
        """Save favorite to database with validation."""
        # Validate form first
        if not self.validate_name():
            return
        
        try:
            favorite_data = self.get_favorite_data()
            
            # Determine the item ID for database reference
            item_id = None
            if self.sequence_type == "sequence":
                item_id = self.sequence_data.get("id")
            elif self.sequence_type == "flow":
                item_id = self.sequence_data.get("id")
            elif self.sequence_type == "pose":
                item_id = self.sequence_data.get("id")
            
            # Save to database
            if item_id:
                # Reference-based favorite
                success = create_favorite(favorite_data["name"], self.sequence_type, item_id)
            else:
                # Data-based favorite (for generated sequences)
                success = create_favorite(favorite_data)
            
            if success:
                # Show success and close
                from utils.ui_utils import show_success_message
                show_success_message(self, "Favorite Saved", f"'{favorite_data['name']}' has been saved to favorites!")
                self.accept()
            else:
                show_error_message(self, "Save Failed", "Failed to save favorite. Name may already exist.")
                
        except Exception as e:
            logger.error(f"Error saving favorite: {e}")
            show_error_message(self, "Save Failed", f"Failed to save favorite: {str(e)}")

    def update_summary_display(self):
        """Update the summary display when form changes."""
        new_summary = self.generate_summary_text()
        self.summary_label.setText(new_summary)