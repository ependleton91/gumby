from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QComboBox, QStyle,QHBoxLayout, QDialog
from PyQt6.QtCore import Qt, QTimer
from config import POSES_IMAGE_DIR
from gui.dialogs.completion_dialog import completion_dialog_box
from utils.database_utils import get_all_sequences, create_practice_session, get_db_manager
from utils.ui_utils import show_success_message, show_error_message
from utils.image_utils import load_preview_image, load_pose_image, scale_image_for_display
from datetime import datetime

class PracticeWidget(QWidget):
    def __init__(self):
        super().__init__() 
        self.current_state = "SELECTION"  # or "PRACTICE" or "ACTIVE_PRACTICE"
        self.selected_sequence = None
        self.session_started = False
        self.timer_is_paused = False

        self.cancel_button = QPushButton("Cancel")
        self.select_different_button = QPushButton("Select Different Sequence") 
        self.start_practice_button = QPushButton("Start Practice")
        
        # Create all views
        self.selection_view = self.create_selection_view()
        self.practice_view = self.create_practice_view()
        self.active_practice_view = self.create_active_practice_view()

        # Show appropriate view based on state
        layout = QVBoxLayout()
        layout.addWidget(self.selection_view)
        layout.addWidget(self.practice_view)
        layout.addWidget(self.active_practice_view)
        layout.addWidget(self.start_practice_button)  
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.select_different_button)

        self.setLayout(layout)
        self.update_view()

    def update_view(self):
        if self.current_state == "SELECTION":
            self.selection_view.setVisible(True)
            self.practice_view.setVisible(False)
            self.active_practice_view.setVisible(False)
            self.update_buttons_for_selection()
        elif self.current_state == "PRACTICE":
            self.selection_view.setVisible(False) 
            self.active_practice_view.setVisible(False)
            self.practice_view.setVisible(True)
            self.update_buttons_for_practice()
        elif self.current_state == "ACTIVE_PRACTICE":
            self.selection_view.setVisible(False) 
            self.practice_view.setVisible(False)
            self.active_practice_view.setVisible(True)
            self.update_buttons_for_active_practice()

    def load_sequences(self):
        """Load sequences from database."""
        try:
            return get_all_sequences()
        except Exception as e:
            print(f"Error loading sequences: {e}")
            return []

    def on_sequence_selected(self, sequence):
        """Handle sequence selection."""
        print(f"Sequence Selected: {sequence['name']}")
        self.selected_sequence = sequence
        self.current_state = "PRACTICE"
        self.update_view()
        
        # Get first pose from sequence for preview
        first_pose = self.get_first_pose_from_sequence(sequence)
        if first_pose:
            raw_image = load_pose_image(first_pose["name"], POSES_IMAGE_DIR)
            scaled_image = scale_image_for_display(raw_image, 300, 400)
            self.practice_image_label.setPixmap(scaled_image)
            self.practice_view_label.setText(first_pose["name"])
        else:
            self.practice_view_label.setText("No poses found in sequence")

    def get_first_pose_from_sequence(self, sequence):
        """Extract the first pose from a sequence's flows."""
        flows = sequence.get("flows", {})
        
        # Try different section types to find the first pose
        section_order = ["warm_up", "main_flow", "standing_flow", "seated_flow", "cool_down"]
        
        for section in section_order:
            if section in flows and flows[section]:
                first_flow = flows[section][0]
                flow_name = first_flow.get("name", "")
                
                # Get the actual flow data with poses
                flow_data = self.get_flow_with_poses(flow_name)
                if flow_data and flow_data.get("flow"):
                    return flow_data["flow"][0]  # Return first pose
        
        return None

    def get_flow_with_poses(self, flow_name):
        """Get flow data including poses from database."""
        try:
            from utils.database_utils import get_db_manager
            
            db = get_db_manager()
            with db.get_connection() as conn:
                # Get flow ID
                cursor = conn.execute("SELECT id FROM flows WHERE name = ?", (flow_name,))
                result = cursor.fetchone()
                if not result:
                    return None
                
                flow_id = result["id"]
                
                # Get poses in this flow
                cursor = conn.execute("""
                    SELECT p.name, COALESCE(fp.pose_duration, p.default_duration) as duration, 
                           p.type, fp.sequence_order
                    FROM flow_poses fp
                    JOIN poses p ON fp.pose_id = p.id
                    WHERE fp.flow_id = ?
                    ORDER BY fp.sequence_order
                """, (flow_id,))
                
                poses = []
                for row in cursor.fetchall():
                    poses.append({
                        "name": row["name"],
                        "duration": row["duration"],
                        "type": row["type"]
                    })
                
                return {"flow": poses} if poses else None
                
        except Exception as e:
            print(f"Error getting flow poses: {e}")
            return None

    def update_buttons_for_selection(self):
        self.cancel_button.setVisible(False)
        self.select_different_button.setVisible(False)
        self.start_practice_button.setVisible(False)

    def update_buttons_for_practice(self):
        self.cancel_button.setVisible(True)
        self.select_different_button.setVisible(True)
        self.start_practice_button.setVisible(True)

    def update_buttons_for_active_practice(self):
        self.cancel_button.setVisible(True)
        self.select_different_button.setVisible(False)
        self.start_practice_button.setVisible(False)

    def create_selection_view(self):
        selection_widget = QWidget()
        layout = QVBoxLayout()
        
        sequences_data = self.load_sequences()
        
        if len(sequences_data) == 0:
            # No sequences case
            header = QLabel("No Sequences Yet!")
            header.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
            message = QLabel("Generate a sequence first to start practicing.")
            message.setStyleSheet("font-size: 14px; margin: 10px;")
            generate_button = QPushButton("Go to Generator")
            generate_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 14px;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    margin: 10px;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            generate_button.clicked.connect(self.go_to_generator)
            
            layout.addWidget(header)
            layout.addWidget(message)
            layout.addWidget(generate_button)

            selection_widget.setLayout(layout)
            return selection_widget
        else:
            # Has sequences - show dropdown
            header = QLabel("Choose a sequence to practice:")
            header.setStyleSheet("font-size: 16px; font-weight: bold; margin: 15px;")
            
            self.sequences_dropdown = QComboBox()
            self.sequences_dropdown.setStyleSheet("""
                QComboBox {
                    padding: 8px;
                    font-size: 14px;
                    border: 2px solid #ddd;
                    border-radius: 4px;
                    margin: 10px;
                }
            """)
            
            for sequence in sequences_data:
                display_name = f"{sequence['name']} ({sequence['total_duration']:.0f} min)"
                self.sequences_dropdown.addItem(display_name)
            self.sequences_dropdown.setMaxVisibleItems(20)  
            
            select_button = QPushButton("Select This Sequence")
            select_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-size: 14px;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    margin: 10px;
                }
                QPushButton:hover { background-color: #1976D2; }
            """)
            select_button.clicked.connect(self.select_from_dropdown)
            
            layout.addWidget(header)
            layout.addWidget(self.sequences_dropdown)
            layout.addWidget(select_button)
        
            selection_widget.setLayout(layout)
            return selection_widget

    def go_to_generator(self):
        # Access main window and use existing method
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'generate_button_was_clicked'):
            main_window = main_window.parent()
        
        if main_window and hasattr(main_window, 'generate_button_was_clicked'):
            main_window.generate_button_was_clicked()

    def select_from_dropdown(self):
        sequences_data = self.load_sequences()
        selected_index = self.sequences_dropdown.currentIndex()
        if selected_index >= 0 and selected_index < len(sequences_data):
            selected_sequence = sequences_data[selected_index]
            self.on_sequence_selected(selected_sequence)

    def create_practice_view(self):
        practice_widget = QWidget()
        layout = QVBoxLayout()
        
        self.practice_image_label = QLabel()
        self.practice_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.practice_image_label.setFixedSize(300, 400)
        self.practice_image_label.setStyleSheet("border: 1px solid #ddd; background-color: #f9f9f9;")
        layout.addWidget(self.practice_image_label)
        
        self.practice_view_label = QLabel()
        self.practice_view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.practice_view_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.practice_view_label)

        practice_widget.setLayout(layout)

        # Connect button events
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.start_practice_button.clicked.connect(self.on_start_practice_clicked)
        self.select_different_button.clicked.connect(self.on_select_different_clicked)

        return practice_widget
    
    def create_active_practice_view(self):
        active_practice_widget = QWidget()
        layout = QVBoxLayout()
        
        self.practice_timer = QTimer()

        self.pause_button = QPushButton()
        self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.pause_button.clicked.connect(self.pause_practice)

        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.resume_practice)

        self.next_pose_text = QLabel("NEXT POSE: --")
        self.next_pose_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_pose_text.setStyleSheet("font-size: 12px; color: #666;")

        self.go_back_arrow = QPushButton()
        self.go_back_arrow.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.go_back_arrow.clicked.connect(self.on_back_clicked)

        self.go_forward_arrow = QPushButton()
        self.go_forward_arrow.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.go_forward_arrow.clicked.connect(self.on_forward_clicked)

        # Display components
        self.active_pose_name = QLabel("CURRENT POSE")
        self.active_pose_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_pose_name.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        
        self.active_pose_image = QLabel() 
        self.active_pose_image.setFixedSize(300, 300)
        self.active_pose_image.setStyleSheet("border: 2px solid #333; background-color: #f5f5f5;")
        self.active_pose_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_display = QLabel("00:30")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_display.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3; margin: 10px;")
        
        self.progress_label = QLabel("1 of --")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 14px; color: #666;")
        
        # Layout setup
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.go_back_arrow)
        image_layout.addWidget(self.active_pose_image)
        image_layout.addWidget(self.go_forward_arrow)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)

        # Add to main vertical layout
        layout.addWidget(self.timer_display)
        layout.addWidget(self.active_pose_name)
        layout.addLayout(image_layout)
        layout.addWidget(self.next_pose_text)
        layout.addLayout(controls_layout)
        layout.addWidget(self.progress_label)

        active_practice_widget.setLayout(layout)
        return active_practice_widget

    def on_start_practice_clicked(self):
        """Start the active practice session."""
        print("Practice started.")
        self.session_started = True
        self.current_state = "ACTIVE_PRACTICE"
        self.session_start_time = datetime.now()

        # Build list of all poses from sequence
        self.list_of_poses = self.build_poses_list_from_sequence(self.selected_sequence)
        
        if not self.list_of_poses:
            show_error_message(self, "No Poses", "This sequence contains no poses to practice.")
            self.current_state = "SELECTION"
            self.update_view()
            return

        self.current_pose_index = 0
        current_pose_info = self.get_current_pose_info(self.current_pose_index)
        
        # Set timer variables
        self.timer_display.setText(f"{current_pose_info['pose_duration_seconds']// 60:02d}:{current_pose_info['pose_duration_seconds'] % 60:02d}")
        self.practice_timer.timeout.connect(self.update_timer_display)
        self.practice_timer.start(1000) 

        # Update widget content
        self.active_pose_name.setText(current_pose_info["current_pose"]["name"])        
        self.progress_label.setText(f"Pose {self.current_pose_index + 1} of {len(self.list_of_poses)}")
        
        if current_pose_info["next_pose"]:          
            self.next_pose_text.setText(f"Next: {current_pose_info['next_pose']['name']}")
        else:
            self.next_pose_text.setText("Next: End of sequence")

        # Load current image
        pose_name = current_pose_info["current_pose"]["name"]
        raw_image = load_pose_image(pose_name, POSES_IMAGE_DIR)
        scaled_image = scale_image_for_display(raw_image, 300, 300)
        self.active_pose_image.setPixmap(scaled_image)
        self.remaining_seconds = current_pose_info["pose_duration_seconds"]

        self.update_view()

    def build_poses_list_from_sequence(self, sequence):
        """Build a flat list of poses from sequence flows."""
        poses_list = []
        flows = sequence.get("flows", {})
        
        # Process flows in logical order
        section_order = ["warm_up", "main_flow", "standing_flow", "seated_flow", 
                        "hip_opener", "backbend_flow", "twist_flow", "cool_down"]
        
        for section in section_order:
            if section in flows:
                for flow_info in flows[section]:
                    flow_name = flow_info.get("name", "")
                    flow_data = self.get_flow_with_poses(flow_name)
                    
                    if flow_data and flow_data.get("flow"):
                        for pose in flow_data["flow"]:
                            poses_list.append({
                                "name": pose["name"],
                                "duration": pose["duration"],
                                "type": pose.get("type", "")
                            })
        
        print(f"Built poses list with {len(poses_list)} poses")
        return poses_list

    def load_pose_image(self, pose_name):
        print(f"Grabbing image for Pose: [{pose_name}]")
        return load_preview_image(pose_name, POSES_IMAGE_DIR)
    
    def on_cancel_clicked(self):
        print("Cancel button clicked.")
        selection = QMessageBox.question(
            self, 
            "Cancel Session", 
            "Are you sure you want to cancel this practice session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if selection == QMessageBox.StandardButton.Yes:
            if self.session_started:
                self.practice_timer.stop()
            self.current_state = "SELECTION"
            self.session_started = False
            self.update_view()

    def on_select_different_clicked(self):
        print("Select different sequence clicked.")
        self.current_state = "SELECTION"
        self.update_view()

    def update_timer_display(self):
        if self.remaining_seconds <= 0:
            self.load_next_pose()
        else:
            self.remaining_seconds -= 1
            self.timer_display.setText(f"{self.remaining_seconds// 60:02d}:{self.remaining_seconds % 60:02d}")

    def get_current_pose_info(self, current_pose_index):
        current_pose_info = {}
        current_pose_info["current_pose"] = self.list_of_poses[current_pose_index]
        current_pose_info["pose_duration_seconds"] = int(current_pose_info["current_pose"]["duration"] * 60)        
        current_pose_info["next_pose"] = self.list_of_poses[current_pose_index + 1] if current_pose_index + 1 < len(self.list_of_poses) else None
        return current_pose_info
    
    def load_next_pose(self):
        self.current_pose_index += 1
        if self.current_pose_index < len(self.list_of_poses):
            current_pose_info = self.get_current_pose_info(self.current_pose_index)

            self.timer_display.setText(f"{current_pose_info['pose_duration_seconds']// 60:02d}:{current_pose_info['pose_duration_seconds'] % 60:02d}")
            self.practice_timer.start(1000) 

            self.active_pose_name.setText(current_pose_info["current_pose"]["name"])        
            self.progress_label.setText(f"Pose {self.current_pose_index + 1} of {len(self.list_of_poses)}")
            
            if current_pose_info["next_pose"] is not None:          
                self.next_pose_text.setText(f"Next: {current_pose_info['next_pose']['name']}")
            else:
                self.next_pose_text.setText("Next: End of sequence")

            # Load current image
            pose_name = current_pose_info["current_pose"]["name"]
            raw_image = load_pose_image(pose_name, POSES_IMAGE_DIR)
            scaled_image = scale_image_for_display(raw_image, 300, 300)
            self.active_pose_image.setPixmap(scaled_image)
            self.remaining_seconds = current_pose_info["pose_duration_seconds"]
        else:
            self.end_of_class()
    
    def on_back_clicked(self):
        print("User clicked back button.")
        if self.current_pose_index > 0:
            self.current_pose_index -= 2  # Go back one (will be incremented in load_next_pose)
            self.load_next_pose()

    def on_forward_clicked(self):
        print("User clicked forward button")
        if self.current_pose_index < (len(self.list_of_poses) - 1):
            self.load_next_pose()
        else:
            self.end_of_class()

    def pause_practice(self):
        self.timer_is_paused = True
        self.practice_timer.stop()
        self.toggle_pause_play_buttons()
    
    def resume_practice(self):
        self.timer_is_paused = False
        self.practice_timer.start(1000) 
        self.toggle_pause_play_buttons()

    def toggle_pause_play_buttons(self):
        if self.timer_is_paused:
            self.pause_button.setEnabled(False)
            self.play_button.setEnabled(True)
        else:
            self.pause_button.setEnabled(True)
            self.play_button.setEnabled(False)

    def end_of_class(self):
        print("Class complete!")
        self.practice_timer.stop()

        completion_dialog = QMessageBox()
        completion_dialog.setWindowTitle("Practice Complete!")
        completion_dialog.setText("Congratulations! You've completed your yoga session. Would you like to save this session to your practice history?")
        completion_dialog.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel)

        if completion_dialog.exec() == QMessageBox.StandardButton.Save:
            # User wants to save session
            dialog = completion_dialog_box(self.selected_sequence, self.session_start_time)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Extract data from dialog
                rating = dialog.rating_field.text()
                notes = dialog.notes_field.toPlainText()
                # Save to practice history              
                self.save_practice_session(rating, notes)
    
        self.current_state = "SELECTION"
        self.session_started = False
        self.update_view()

    def save_practice_session(self, rating, notes):
        """Save practice session to database."""
        try:
            # Validate rating
            try:
                rating_int = int(rating)
                if rating_int < 1 or rating_int > 5:
                    rating_int = 3  # Default to middle rating
            except ValueError:
                rating_int = 3 

            # Calculate actual duration
            session_end_time = datetime.now()
            actual_duration = (session_end_time - self.session_start_time).total_seconds() / 60

            # Get sequence ID
            sequence_id = self.selected_sequence.get("id")
            if not sequence_id:
                show_error_message(self, "Save Error", "Could not save session - sequence ID not found.")
                return

            # Create session data
            session_data = {
                "sequence_id": sequence_id,
                "duration_minutes": actual_duration,
                "rating": rating_int,
                "notes": notes or ""
            }

            # Save to database
            if create_practice_session(session_data):
                show_success_message(
                    self, 
                    "Session Saved", 
                    f"Practice session saved successfully!\n"
                    f"Duration: {actual_duration:.1f} minutes\n"
                    f"Rating: {rating_int}/5"
                )
            else:
                show_error_message(self, "Save Failed", "Failed to save practice session. Please try again.")

        except Exception as e:
            print(f"Error saving practice session: {e}")
            show_error_message(self, "Save Error", f"Error saving session: {str(e)}")

    def refresh_sequences(self):
        """Refresh the sequences list from database."""
        if self.current_state == "SELECTION":
            # Rebuild selection view with updated data
            new_selection_view = self.create_selection_view()
            
            # Replace old selection view
            self.layout().replaceWidget(self.selection_view, new_selection_view)
            self.selection_view.deleteLater()
            self.selection_view = new_selection_view
            
            self.update_view()