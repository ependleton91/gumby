from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QHBoxLayout, QMessageBox
from gui.dialogs.details_dialog import details_dialog_box
from utils.ui_utils import show_error_message, show_success_message, confirm_sequence_delete
from utils.database_utils import get_all_favorites, delete_favorite, get_favorite_by_name
from utils.datetime_utils import format_time_ago
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class FavoritesWidget(QWidget):
    def create_favorites_display(self):
        # Create scrollable area for favorites
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        # Load favorites data from normalized database
        favorites_list = get_all_favorites()

        if len(favorites_list) == 0:
            empty_message = QLabel("No favorites saved yet. Generate a sequence and favorite it!")
            empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_message.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
            scroll_layout.addWidget(empty_message)
        else:
            # Generate Favorites
            for favorite in favorites_list:
                card_widget = self.create_favorite_card(favorite)
                scroll_layout.addWidget(card_widget)

        # Set scroll area properties
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
           
        return scroll_area

    def create_favorite_card(self, favorite):
        """Create a card widget for a single favorite."""
        card_widget = QWidget()
        card_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
        """)
        card_layout = QVBoxLayout()

        # Favorite name
        name_label = QLabel(favorite["name"])
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E86AB;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Metadata (type, creation date)
        meta_info = self.format_favorite_metadata(favorite)
        meta_info_label = QLabel(meta_info)
        meta_info_label.setStyleSheet("color: #666; font-size: 12px;")
        meta_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Content preview (expandable)
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Expand/collapse button
        expand_btn = QPushButton("▶ Show Details")
        expand_btn.clicked.connect(lambda checked, widget=content_widget, btn=expand_btn: self.toggle_content(widget, btn))

        # Content details (initially hidden)
        content_details = self.format_favorite_content(favorite)
        content_label = QLabel(content_details)
        content_label.setStyleSheet("""
            font-family: monospace; 
            padding: 10px; 
            background-color: #ffffff; 
            border: 1px solid #dee2e6;
            border-radius: 4px; 
            line-height: 1.4;
        """)
        content_label.setWordWrap(True)

        content_layout.addWidget(content_label)
        content_widget.setLayout(content_layout)
        content_widget.setVisible(False)  # Start collapsed

        # Action buttons
        button_layout = QHBoxLayout()
        details_btn = QPushButton("View Details")
        practice_btn = QPushButton("Practice")
        delete_btn = QPushButton("Delete")
        
        # Style buttons
        details_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px; border-radius: 4px;")
        practice_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px; border-radius: 4px;")
        delete_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 8px 16px; border-radius: 4px;")

        # Connect buttons
        details_btn.clicked.connect(lambda checked, fav=favorite: self.show_details(fav))
        practice_btn.clicked.connect(lambda checked, fav=favorite: self.start_practice(fav))
        delete_btn.clicked.connect(lambda checked, fav=favorite: self.delete_favorite(fav))

        button_layout.addWidget(details_btn)
        button_layout.addWidget(practice_btn)
        button_layout.addWidget(delete_btn)

        # Add everything to card
        card_layout.addWidget(name_label)
        card_layout.addWidget(meta_info_label)
        card_layout.addWidget(expand_btn)
        card_layout.addWidget(content_widget)
        card_layout.addLayout(button_layout)

        card_widget.setLayout(card_layout)
        return card_widget

    def format_favorite_metadata(self, favorite):
        """Format metadata information for display."""
        favorite_type = favorite.get("type", "sequence").title()
        created_date = favorite.get("created_at", "Unknown")
        
        # Format the creation time
        try:
            time_ago = format_time_ago(created_date)
            return f"Type: {favorite_type} | Created: {time_ago}"
        except:
            return f"Type: {favorite_type} | Created: {created_date}"

    def format_favorite_content(self, favorite):
        """Format favorite content based on type."""
        favorite_type = favorite.get("type", "sequence")
        
        if favorite_type == "pose":
            return self.format_pose_favorite_content(favorite)
        elif favorite_type == "flow":
            return self.format_flow_favorite_content(favorite)
        elif favorite_type == "sequence":
            return self.format_sequence_favorite_content(favorite)
        else:
            return "Unknown favorite type"

    def format_pose_favorite_content(self, favorite):
        """Format pose favorite content."""
        pose_data = favorite.get("pose_data", {})
        if not pose_data:
            return "Pose data not available"
        
        content = f"Pose: {pose_data.get('name', 'Unknown')}\n"
        content += f"Duration: {pose_data.get('default_duration', 0)} minutes\n"
        content += f"Difficulty: {pose_data.get('difficulty', 1)}/5\n"
        content += f"Type: {pose_data.get('type', 'Unknown')}\n"
        
        muscle_groups = pose_data.get('muscle_groups', [])
        if muscle_groups:
            content += f"Targets: {', '.join(muscle_groups)}\n"
        
        description = pose_data.get('description', '')
        if description:
            content += f"\nDescription: {description[:100]}..."
        
        return content

    def format_flow_favorite_content(self, favorite):
        """Format flow favorite content."""
        flow_data = favorite.get("flow_data", {})
        if not flow_data:
            return "Flow data not available"
        
        content = f"Flow: {flow_data.get('name', 'Unknown')}\n"
        content += f"Duration: {flow_data.get('duration', 0)} minutes\n"
        content += f"Difficulty: {flow_data.get('difficulty', 1)}/5\n"
        content += f"Category: {flow_data.get('category', 'Unknown')}\n"
        content += f"Energy: {flow_data.get('energy_level', 'Unknown')}\n"
        
        # Show pose count if available
        poses = flow_data.get('flow', [])
        if poses:
            content += f"Poses: {len(poses)} poses\n"
            # Show first few pose names
            pose_names = [pose.get('name', '') for pose in poses[:3]]
            if pose_names:
                content += f"Includes: {', '.join(pose_names)}"
                if len(poses) > 3:
                    content += f" and {len(poses) - 3} more..."
        
        return content

    def format_sequence_favorite_content(self, favorite):
        """Format sequence favorite content."""
        # Handle both old and new data structures
        flows_data = favorite.get("flows", [])
        if not flows_data:
            return "Sequence data not available"
        
        content = ""
        flow_count = 0
        
        if isinstance(flows_data, list):
            # New normalized structure - list of flows
            content += f"Complete Sequence ({len(flows_data)} flows)\n\n"
            for i, flow in enumerate(flows_data, 1):
                flow_name = flow.get('name', 'Unknown Flow')
                flow_duration = flow.get('duration', 0)
                content += f"{i}. {flow_name} ({flow_duration:.1f} min)\n"
        
        elif isinstance(flows_data, dict):
            # Old structure - flows organized by section
            section_map = {
                "warm_up": "WARM UP",
                "main_flow": "MAIN FLOW", 
                "cool_down": "COOL DOWN"
            }
            
            for section_key, flow_list in flows_data.items():
                if flow_list:
                    content += f"=== {section_map.get(section_key, section_key.upper())} ===\n"
                    for flow in flow_list:
                        flow_count += 1
                        flow_name = flow.get('name', 'Unknown Flow')
                        content += f"{flow_count}. {flow_name}\n"
                    content += "\n"
        
        return content.strip()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.scroll_area = self.create_favorites_display()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def refresh_favorites(self):
        """Refresh the favorites display."""
        self.layout().removeWidget(self.scroll_area)
        self.scroll_area.deleteLater()
        new_scroll_area = self.create_favorites_display()
        self.layout().addWidget(new_scroll_area)
        self.scroll_area = new_scroll_area

    def toggle_content(self, content_widget, button):
        """Toggle content visibility and update button text."""
        if content_widget.isVisible():
            content_widget.setVisible(False)
            button.setText("▶ Show Details")
        else:
            content_widget.setVisible(True)
            button.setText("▼ Hide Details")

    def delete_favorite(self, favorite):
        """Delete a favorite with confirmation."""
        favorite_name = favorite["name"]
        favorite_id = favorite.get("id")
        
        if not favorite_id:
            show_error_message(self, "Error", "Cannot delete favorite: missing ID")
            return
        
        if confirm_sequence_delete(self, favorite_name):
            # Delete from normalized database
            if delete_favorite(favorite_id):
                show_success_message(self, "Favorite Deleted", f"Successfully deleted '{favorite_name}' from favorites.")
                self.refresh_favorites()
            else:
                show_error_message(self, "Deletion Failed", f"Failed to delete '{favorite_name}' from favorites.")

    def start_practice(self, favorite):
        """Start practice session with this favorite."""
        # Navigate to practice mode with this favorite pre-selected
        main_window = self.parent().parent()
        if hasattr(main_window, 'practice_button_was_clicked'):
            main_window.practice_button_was_clicked()
            # TODO: Pass favorite to practice widget for pre-selection
            if hasattr(main_window, 'practice_widget'):
                # This would require updating practice_widget to accept pre-selected favorites
                pass

    def show_details(self, favorite):
        """Show detailed favorite information in dialog."""
        try:
            dialog = details_dialog_box(favorite)
            dialog.exec()
            self.refresh_favorites()
        except Exception as e:
            show_error_message(self, "Error", f"Could not open favorite details: {str(e)}")

    def get_favorites_summary(self):
        """Get summary statistics for favorites."""
        try:
            favorites_list = get_all_favorites()
            
            total_count = len(favorites_list)
            type_counts = {}
            
            for favorite in favorites_list:
                fav_type = favorite.get("type", "unknown")
                type_counts[fav_type] = type_counts.get(fav_type, 0) + 1
            
            return {
                "total": total_count,
                "by_type": type_counts
            }
        except Exception as e:
            logger.error(f"Error getting favorites summary: {e}")
            return {"total": 0, "by_type": {}}