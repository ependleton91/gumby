from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QComboBox, QStyle,QHBoxLayout, QDialog
from PyQt6.QtCore import Qt, QTimer
from config import POSES_IMAGE_DIR
from gui.dialogs.completion_dialog import completion_dialog_box
from utils.file_utils import load_favorites_data, save_favorites_data
from utils.ui_utils import show_success_message, show_error_message
from utils.image_utils import load_preview_image,load_pose_image,scale_image_for_display
from datetime import datetime

class PracticeWidget(QWidget):
    def __init__(self):
        super().__init__() 
        self.current_state = "SELECTION"  # or "PRACTICE" 
        self.selected_favorite = None
        self.session_started = False

        self.cancel_button = QPushButton("Cancel")
        self.select_different_button = QPushButton("Select Different Sequence") 
        self.start_practice_button = QPushButton("Start Practice")
        
        # Create both views
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

    def load_favorites(self):
        data = load_favorites_data()
        return data.get("favorites", [])

        
    def on_favorite_selected(self, favorite):
        print(f"Sequence Selected: {favorite["name"]}")
        self.selected_favorite = favorite
        self.current_state = "PRACTICE"
        self.update_view()
        
        pose_name = favorite["sequences"]["warm_up"][0]["flow"][0]["name"]
        raw_image = load_pose_image(pose_name, POSES_IMAGE_DIR)
        scaled_image = scale_image_for_display(raw_image, 300, 400)  # Fit in 300x400 label
        self.practice_image_label.setPixmap(scaled_image)
            

        self.practice_view_label.setText(favorite["sequences"]["warm_up"][0]["flow"][0]["name"])

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
        
        favorites_data = self.load_favorites()
        
        if len(favorites_data) == 0:
            # No favorites case
            header = QLabel("No Favorites Yet!")
            message = QLabel("Generate a sequence and save it as a favorite first.")
            generate_button = QPushButton("Go to Generator")
            generate_button.clicked.connect(self.go_to_generator)
            
            layout.addWidget(header)
            layout.addWidget(message)
            layout.addWidget(generate_button)
        else:
            # Has favorites - show dropdown
            header = QLabel("Choose a sequence to practice:")
            
            self.favorites_dropdown = QComboBox()
            for favorite in favorites_data:
                self.favorites_dropdown.addItem(favorite["name"])
            self.favorites_dropdown.setMaxVisibleItems(20)  
            
            select_button = QPushButton("Select This Sequence")
            select_button.clicked.connect(self.select_from_dropdown)
            
            layout.addWidget(header)
            layout.addWidget(self.favorites_dropdown)
            layout.addWidget(select_button)
        
            selection_widget.setLayout(layout)
            return selection_widget

    def go_to_generator(self):
        # Access main window and use existing method
        main_window = self.parent().parent()  # Navigate up to MainWindow
        main_window.generate_button_was_clicked()

    def select_from_dropdown(self):
        favorites_data = self.load_favorites()
        selected_index = self.favorites_dropdown.currentIndex()
        selected_favorite = favorites_data[selected_index]
        self.on_favorite_selected(selected_favorite)

    def create_practice_view(self):

        practice_widget=QWidget()
        layout = QVBoxLayout()
        practice_widget.setLayout(layout)
        self.practice_image_label = QLabel()
        self.practice_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.practice_image_label.setFixedSize(300,400)
        layout.addWidget(self.practice_image_label)
        self.practice_view_label = QLabel()
        layout.addWidget(self.practice_view_label)

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

        self.next_pose_text = QLabel(f"NEXT POSE: xx")

        self.go_back_arrow = QPushButton()
        self.go_back_arrow.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.go_back_arrow.clicked.connect(self.on_back_clicked)

        self.go_forward_arrow = QPushButton()
        self.go_forward_arrow.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.go_forward_arrow.clicked.connect(self.on_forward_clicked)

            
        # Add display components:
        self.active_pose_name = QLabel("CURRENT POSE")
        self.active_pose_image = QLabel() 
        self.active_pose_image.setFixedSize(300, 300)  

        self.timer_display = QLabel("00:30")
        self.progress_label = QLabel("1 out of xx")
        
        # Add everything to layout:
        # Image section with arrows
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.go_back_arrow)
        image_layout.addWidget(self.active_pose_image)
        image_layout.addWidget(self.go_forward_arrow)

        # Play/pause section  
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.cancel_button)
        bottom_layout.addWidget(self.select_different_button)

        # Add to main vertical layout
        layout.addWidget(self.timer_display)
        layout.addWidget(self.active_pose_name)
        layout.addLayout(image_layout)  # Note: addLayout, not addWidget
        layout.addWidget(self.next_pose_text)
        layout.addLayout(controls_layout)
        layout.addWidget(self.progress_label)
        layout.addLayout(bottom_layout)

        active_practice_widget.setLayout(layout)
        return active_practice_widget

    def on_start_practice_clicked(self):
        print("Practice started.")
        self.session_started = True
        self.current_state = "ACTIVE_PRACTICE"
        self.session_start_time = datetime.now()

        
        #flatten list to grab all poses
        self.list_of_poses = []
        for section_key, sequence_list in self.selected_favorite['sequences'].items():
            for sequence in sequence_list:
                for pose in sequence["flow"]:
                    pose_info = {
                        "name": pose["name"],
                        "duration": pose["duration"],
                        "type": pose["type"]
                        }
                    self.list_of_poses.append(pose_info)
            

        self.current_pose_index = 0
        #grab pose info
        
        current_pose_info = self.get_current_pose_info(self.current_pose_index)
        
        #Set timer variables
        self.timer_display.setText(f"{current_pose_info["pose_duration_seconds"]// 60:02d}:{current_pose_info["pose_duration_seconds"] % 60:02d}")
        self.practice_timer.timeout.connect(self.update_timer_display)
        self.practice_timer.start(1000) 

        # Update widget content
        self.active_pose_name.setText(current_pose_info["current_pose"]["name"])        
        self.progress_label.setText(f"Pose {str(self.current_pose_index + 1)} of {str(len(self.list_of_poses))}")
        if current_pose_info["next_pose"]["name"]:          
            self.next_pose_text.setText(f"Next: {current_pose_info["next_pose"]["name"]}")

        #Grab current image
        pose_name = current_pose_info["current_pose"]["name"]
        raw_image = load_pose_image(pose_name, POSES_IMAGE_DIR)
        scaled_image = scale_image_for_display(raw_image, 300, 300)  # Fit in 300x300 label
        self.active_pose_image.setPixmap(scaled_image)
        self.remaining_seconds = current_pose_info["pose_duration_seconds"]

        self.update_view()

    def load_pose_image(self,pose_name):
        print(f"Grabbing image for Pose: [{pose_name}]")
        return load_preview_image(pose_name, POSES_IMAGE_DIR)
    
    def on_cancel_clicked(self):
        print(f"Cancel button clicked.")
        selection = QMessageBox.question(
            self, 
            "Cancel Session", 
            f"Are you sure you want to cancel this practice session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
            )

        if selection == QMessageBox.StandardButton.Yes and self.session_started == True:
            self.current_state = "SELECTION"
            self.update_view()
        elif selection == QMessageBox.StandardButton.Yes and self.session_started == False:
            main_window = self.parent().parent()  # Navigate up to MainWindow
            main_window.back_to_main()

        else:
            return

    def on_select_different_clicked(self):
        print("select a different sequence clicked.")
        self.current_state = "SELECTION"
        self.update_view()

    def update_timer_display(self):
        
        if self.remaining_seconds == 0:
            self.load_next_pose()
        else:
            self.remaining_seconds -= 1
            self.timer_display.setText(f"{self.remaining_seconds// 60:02d}:{self.remaining_seconds % 60:02d}")

    def get_current_pose_info(self,current_pose_index):
        current_pose_info = {}
        current_pose_info["current_pose"] = self.list_of_poses[current_pose_index]  # ✅
        current_pose_info["pose_duration_seconds"] = int(current_pose_info["current_pose"]["duration"] * 60)        
        current_pose_info["next_pose"] = self.list_of_poses[current_pose_index + 1] if current_pose_index + 1 < len(self.list_of_poses) else None  # ✅
        return current_pose_info
    
    def load_next_pose(self):
        self.current_pose_index+= 1
        if self.current_pose_index < len(self.list_of_poses):
            current_pose_info = self.get_current_pose_info(self.current_pose_index)

            self.timer_display.setText(f"{current_pose_info["pose_duration_seconds"]// 60:02d}:{current_pose_info["pose_duration_seconds"] % 60:02d}")
            self.practice_timer.start(1000) 

            self.active_pose_name.setText(current_pose_info["current_pose"]["name"])        
            self.progress_label.setText(f"Pose {str(self.current_pose_index + 1)} of {str(len(self.list_of_poses))}")
            
            if current_pose_info["next_pose"] is not None:          
                self.next_pose_text.setText(f"Next: {current_pose_info["next_pose"]["name"]}")

            #Grab current image
            pose_name = current_pose_info["current_pose"]["name"]
            raw_image = load_pose_image(pose_name, POSES_IMAGE_DIR)
            scaled_image = scale_image_for_display(raw_image, 300, 300)  # Fit in 300x300 label
            self.active_pose_image.setPixmap(scaled_image)
            self.remaining_seconds = current_pose_info["pose_duration_seconds"]
        else:
            self.end_of_class()
    
    def on_back_clicked(self):
        print("User clicked back button.")
        if self.current_pose_index>0:
            self.current_pose_index-=2
            self.load_next_pose()
        else:
            return

    def on_forward_clicked(self):
        print("user clicked forward button")
        if self.current_pose_index < (len(self.list_of_poses)-1):
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
        if self.timer_is_paused == True:
            self.pause_button.setEnabled(False)
            self.play_button.setEnabled(True)
            self.update_view()
        else:
            self.pause_button.setEnabled(True)
            self.play_button.setEnabled(False)
            self.update_view()

    def end_of_class(self):
        print("Class complete!")
        self.practice_timer.stop()

        completion_dialog = QMessageBox()
        completion_dialog.setWindowTitle("Practice Complete!")
        completion_dialog.setText("Congratulations! You've completed your yoga session. Would you like to save this session to your practice history?")
        completion_dialog.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel)

        if completion_dialog.exec() == QMessageBox.StandardButton.Save:
        # User wants to save session
            dialog = completion_dialog_box(self.selected_favorite,self.session_start_time)
            if dialog.exec() == QDialog.DialogCode.Accepted:  # User clicked Save
                 # Extract data from dialog
                rating = dialog.rating_field.text()
                notes = dialog.notes_field.toPlainText()
                date = dialog.date_field.text()
                # Save to practice history              
                self.save_practice_session(rating, notes, date)
        # Else just return to selection
    
        self.current_state = "SELECTION"
        self.session_started = False
        self.update_view()

    def save_practice_session(self,rating,notes,date):

        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                rating_int = 3  # Default to middle rating
        except ValueError:
            rating_int = 3 
        
        favorites_data = load_favorites_data()


        for item in favorites_data["favorites"]:
            if "practice_history" not in item:
                item["practice_history"] = []
            if item['name'] == self.selected_favorite['name']:
               item["practice_history"].append({"date": str(date), "rating": int(rating), "notes": notes})  
               break

        practice_saved = save_favorites_data(favorites_data)
        if practice_saved:
            show_success_message("Practice session ")
        else:
            show_error_message("Failed to save practice session. Please try again.")
        