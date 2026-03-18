from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QCheckBox, QGroupBox, QFrame,
    QApplication, QDialog, QProgressBar, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from utils.database_utils import (
    get_all_poses, get_all_flows, create_pose, update_pose, delete_pose,
    get_all_muscle_groups, get_all_yoga_styles
)
from utils.image_utils import load_thumbnail_image, clear_image_cache, create_placeholder_image
from utils.ui_utils import (
    show_error_message, show_success_message, confirm_destructive_action,
    hide_widgets, show_widgets, show_save_success
)
from utils.display_utils import format_list_for_display, format_for_internal
from utils.validation_utils import validate_new_pose_data
from config import POSES_IMAGE_DIR
# Import your pose dialog - adjust path as needed
try:
    from gui.dialogs.pose_details_dialog import pose_details_box
except ImportError:
    # Fallback if the dialog is in a different location
    try:
        from .pose_details_dialog import pose_details_box
    except ImportError:
        # Create a placeholder dialog class
        from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
        class pose_details_box(QDialog):
            def __init__(self, pose_info, edit_mode=False, create_mode=False):
                super().__init__()
                self.pose_info = pose_info
                layout = QVBoxLayout()
                layout.addWidget(QLabel("Pose dialog not available"))
                self.setLayout(layout)
            def get_pose_data(self):
                return self.pose_info

import logging
logger = logging.getLogger(__name__)

class ImageLoadThread(QThread):
    """Background thread for loading pose images."""
    image_loaded = pyqtSignal(str, QPixmap)
    
    def __init__(self, pose_names):
        super().__init__()
        self.pose_names = pose_names
        
    def run(self):
        for pose_name in self.pose_names:
            try:
                pixmap = load_thumbnail_image(pose_name, POSES_IMAGE_DIR)
                self.image_loaded.emit(pose_name, pixmap)
            except Exception as e:
                logger.error(f"Error loading image for {pose_name}: {e}")

class PoseCard(QFrame):
    """Individual pose card widget."""
    
    clicked = pyqtSignal(dict)  # Emits pose data when clicked
    
    def __init__(self, pose_data):
        super().__init__()
        self.pose_data = pose_data
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedSize(160, 200)
        self.setStyleSheet("""
            PoseCard {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                margin: 2px;
            }
            PoseCard:hover {
                border: 2px solid #4CAF50;
                background-color: #f9f9f9;
            }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Pose image
        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 90)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        
        # Load placeholder initially
        placeholder = create_placeholder_image("Loading...", 120, 90)
        self.image_label.setPixmap(placeholder)
        
        # Pose name
        pose_name = self.pose_data.get('name', 'Unknown')
        self.name_label = QLabel(pose_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumHeight(40)
        
        # Info labels
        difficulty = self.pose_data.get('difficulty', 1)
        duration = self.pose_data.get('default_duration', 0)
        
        info_text = f"Level {difficulty} • {duration:.1f}min"
        self.info_label = QLabel(info_text)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 9px; color: #666;")
        
        # Muscle groups (truncated)
        muscles = self.pose_data.get('muscle_groups', [])
        if muscles:
            muscle_text = ', '.join(muscles[:2])  # Show first 2
            if len(muscles) > 2:
                muscle_text += f" +{len(muscles)-2}"
        else:
            muscle_text = "General"
            
        self.muscle_label = QLabel(muscle_text)
        self.muscle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.muscle_label.setStyleSheet("font-size: 8px; color: #888;")
        self.muscle_label.setWordWrap(True)
        
        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.muscle_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_image(self, pixmap):
        """Update the pose image."""
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.pose_data)
        super().mousePressEvent(event)

class FilterPanel(QWidget):
    """Filter controls for poses."""
    
    filters_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Search box
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search poses by name...")
        self.search_box.textChanged.connect(self.emit_filters)
        search_layout.addWidget(self.search_box)
        search_group.setLayout(search_layout)
        
        # Difficulty filter
        difficulty_group = QGroupBox("Difficulty")
        difficulty_layout = QVBoxLayout()
        
        self.difficulty_checkboxes = []
        for i in range(1, 6):
            checkbox = QCheckBox(f"Level {i}")
            checkbox.setChecked(True)  # Start with all checked
            checkbox.stateChanged.connect(self.emit_filters)
            self.difficulty_checkboxes.append(checkbox)
            difficulty_layout.addWidget(checkbox)
            
        difficulty_group.setLayout(difficulty_layout)
        
        # Muscle groups filter
        muscle_group = QGroupBox("Muscle Groups")
        muscle_layout = QVBoxLayout()
        
        self.muscle_checkboxes = []
        try:
            muscles = get_all_muscle_groups()[:10]  # Limit to first 10
            for muscle in muscles:
                checkbox = QCheckBox(muscle.replace("_", " ").title())
                checkbox.muscle_name = muscle
                checkbox.stateChanged.connect(self.emit_filters)
                self.muscle_checkboxes.append(checkbox)
                muscle_layout.addWidget(checkbox)
        except Exception as e:
            muscle_layout.addWidget(QLabel("Muscle filters unavailable"))
            
        muscle_group.setLayout(muscle_layout)
        
        # Clear/Reset buttons
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear All")
        reset_button = QPushButton("Reset All")
        
        clear_button.clicked.connect(self.clear_all_filters)
        reset_button.clicked.connect(self.reset_all_filters)
        
        button_layout.addWidget(clear_button)
        button_layout.addWidget(reset_button)
        
        # Add all to main layout
        layout.addWidget(search_group)
        layout.addWidget(difficulty_group)
        layout.addWidget(muscle_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMaximumWidth(250)
        
    def emit_filters(self):
        """Emit current filter state."""
        filters = self.get_current_filters()
        self.filters_changed.emit(filters)
        
    def get_current_filters(self):
        """Get current filter values."""
        return {
            'search': self.search_box.text().lower(),
            'difficulties': [i+1 for i, cb in enumerate(self.difficulty_checkboxes) if cb.isChecked()],
            'muscles': [cb.muscle_name for cb in self.muscle_checkboxes if cb.isChecked()]
        }
        
    def clear_all_filters(self):
        """Clear all filter selections."""
        self.search_box.clear()
        for cb in self.difficulty_checkboxes:
            cb.setChecked(False)
        for cb in self.muscle_checkboxes:
            cb.setChecked(False)
            
    def reset_all_filters(self):
        """Reset to show all poses."""
        self.search_box.clear()
        for cb in self.difficulty_checkboxes:
            cb.setChecked(True)
        for cb in self.muscle_checkboxes:
            cb.setChecked(False)  # Don't filter by muscle groups by default

class PosesWidget(QWidget):
    """Main poses management widget."""
    
    def __init__(self):
        super().__init__()
        self.poses_data = []
        self.filtered_poses = []
        self.pose_cards = []
        self.image_thread = None
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QHBoxLayout()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Filter panel on left
        self.filter_panel = FilterPanel()
        self.filter_panel.filters_changed.connect(self.apply_filters)
        splitter.addWidget(self.filter_panel)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Yoga Poses")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        
        self.count_label = QLabel("0 poses")
        self.count_label.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        
        # Action buttons
        self.add_pose_button = QPushButton("Add New Pose")
        self.add_pose_button.clicked.connect(self.add_new_pose)
        self.add_pose_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_pose_button)
        header_layout.addWidget(self.refresh_button)
        
        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Poses grid in scroll area
        self.scroll_area = QScrollArea()
        self.poses_container = QWidget()
        self.poses_layout = QGridLayout()
        self.poses_layout.setSpacing(10)
        self.poses_container.setLayout(self.poses_layout)
        
        self.scroll_area.setWidget(self.poses_container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        content_layout.addLayout(header_layout)
        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.scroll_area)
        
        content_widget.setLayout(content_layout)
        splitter.addWidget(content_widget)
        
        # Set splitter proportions
        splitter.setSizes([250, 1000])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def load_data(self):
        """Load poses from database."""
        try:
            self.poses_data = get_all_poses()
            self.filtered_poses = self.poses_data.copy()
            self.update_count_label()
            self.create_pose_cards()
            logger.info(f"Loaded {len(self.poses_data)} poses")
        except Exception as e:
            logger.error(f"Error loading poses: {e}")
            show_error_message(self, "Loading Error", f"Failed to load poses: {str(e)}")
            self.poses_data = []
            self.filtered_poses = []
            
    def refresh_data(self):
        """Refresh poses data from database."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Clear existing cards
        self.clear_pose_cards()
        
        # Reload data
        self.load_data()
        
        self.progress_bar.setVisible(False)
        
    def clear_pose_cards(self):
        """Remove all pose cards from layout."""
        for card in self.pose_cards:
            card.setParent(None)
            card.deleteLater()
        self.pose_cards.clear()
        
    def create_pose_cards(self):
        """Create pose cards for current filtered data."""
        self.clear_pose_cards()
        
        # Calculate grid dimensions
        columns = max(1, (self.scroll_area.width() - 50) // 170)  # Card width + margin
        
        for i, pose in enumerate(self.filtered_poses):
            card = PoseCard(pose)
            card.clicked.connect(self.show_pose_details)
            
            row = i // columns
            col = i % columns
            self.poses_layout.addWidget(card, row, col)
            self.pose_cards.append(card)
            
        # Add stretch to push cards to top-left
        self.poses_layout.setRowStretch(len(self.filtered_poses) // columns + 1, 1)
        
    def load_pose_images(self):
        """Load pose images in background thread."""
        if self.image_thread and self.image_thread.isRunning():
            return
            
        pose_names = [pose['name'] for pose in self.filtered_poses]
        if not pose_names:
            return
            
        self.image_thread = ImageLoadThread(pose_names)
        self.image_thread.image_loaded.connect(self.update_card_image)
        self.image_thread.start()
        
    def update_card_image(self, pose_name, pixmap):
        """Update specific card image."""
        for card in self.pose_cards:
            if card.pose_data.get('name') == pose_name:
                card.update_image(pixmap)
                break
                
    def apply_filters(self, filters):
        """Apply filters to pose list."""
        search_term = filters.get('search', '').lower()
        difficulties = filters.get('difficulties', [])
        muscles = filters.get('muscles', [])
        
        self.filtered_poses = []
        
        for pose in self.poses_data:
            # Search filter
            if search_term and search_term not in pose.get('name', '').lower():
                continue
                
            # Difficulty filter
            if difficulties and pose.get('difficulty', 1) not in difficulties:
                continue
                
            # Muscle filter (if any muscles selected)
            if muscles:
                pose_muscles = pose.get('muscle_groups', [])
                if not any(muscle in pose_muscles for muscle in muscles):
                    continue
                    
            self.filtered_poses.append(pose)
            
        self.update_count_label()
        self.create_pose_cards()
        
        # Load images for visible poses
        QTimer.singleShot(100, self.load_pose_images)
        
    def update_count_label(self):
        """Update the count label."""
        total = len(self.poses_data)
        filtered = len(self.filtered_poses)
        
        if filtered == total:
            self.count_label.setText(f"{total} poses")
        else:
            self.count_label.setText(f"{filtered} of {total} poses")
            
    def show_pose_details(self, pose_data):
        """Show detailed pose information."""
        dialog = pose_details_box(pose_data, edit_mode=False)
        dialog.exec()
        
    def add_new_pose(self):
        """Show dialog to add new pose."""
        empty_pose = {
            "name": "",
            "default_duration": 0.5,
            "type": "main",
            "difficulty": 2,
            "muscle_groups": [],
            "description": "",
            "instructions": "",
            "modifications": "",
            "image_filename": "no_image.png"
        }
        
        dialog = pose_details_box(empty_pose, create_mode=True)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pose_data = dialog.get_pose_data()
            
            try:
                if create_pose(pose_data):
                    show_save_success(self, "Pose", pose_data["name"])
                    self.refresh_data()
                else:
                    show_error_message(self, "Save Failed", "Failed to create pose.")
            except Exception as e:
                logger.error(f"Error creating pose: {e}")
                show_error_message(self, "Save Error", f"Error creating pose: {str(e)}")
                
    def edit_pose(self, pose_data):
        """Edit existing pose."""
        dialog = pose_details_box(pose_data, edit_mode=True)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_pose_data()
            original_name = pose_data["name"]
            
            try:
                if update_pose(original_name, updated_data):
                    show_save_success(self, "Pose", updated_data["name"])
                    self.refresh_data()
                else:
                    show_error_message(self, "Update Failed", "Failed to update pose.")
            except Exception as e:
                logger.error(f"Error updating pose: {e}")
                show_error_message(self, "Update Error", f"Error updating pose: {str(e)}")
                
    def delete_pose(self, pose_data):
        """Delete pose after confirmation."""
        pose_name = pose_data["name"]
        
        if confirm_destructive_action(self, "Delete Pose", 
                                    "Are you sure you want to delete this pose?", 
                                    pose_name):
            try:
                if delete_pose(pose_name):
                    show_success_message(self, "Deleted", f"Pose '{pose_name}' deleted successfully.")
                    self.refresh_data()
                else:
                    show_error_message(self, "Delete Failed", "Failed to delete pose.")
            except Exception as e:
                logger.error(f"Error deleting pose: {e}")
                show_error_message(self, "Delete Error", f"Error deleting pose: {str(e)}")
                
    def resizeEvent(self, event):
        """Handle widget resize to adjust grid layout."""
        super().resizeEvent(event)
        # Recreate cards with new layout when window is resized
        if hasattr(self, 'filtered_poses'):
            QTimer.singleShot(100, self.create_pose_cards)