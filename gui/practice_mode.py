from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QComboBox, QStyle,QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QSize, Qt, QTimer
from config import FAVORITES_FILE, POSES_IMAGE_DIR
import json

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
        try:
            with open(FAVORITES_FILE, 'r') as f:
                data = json.load(f)
            return data.get("favorites", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []  
        
    def on_favorite_selected(self, favorite):
        print(f"Sequence Selected: {favorite["name"]}")
        self.selected_favorite = favorite
        self.current_state = "PRACTICE"
        self.update_view()

        pixmap = self.load_pose_image(favorite["sequences"]["warm_up"][0]["flow"][0]["name"])
        scaled_pixmap = pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        if pixmap is not None:
            self.practice_image_label.setPixmap(scaled_pixmap)
            

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
        pixmap = self.load_pose_image(current_pose_info["current_pose"]["name"])
        if pixmap is not None:
            scaled_pixmap = pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.active_pose_image.setPixmap(scaled_pixmap)
        self.remaining_seconds = current_pose_info["pose_duration_seconds"]

        self.update_view()

    def load_pose_image(self,pose_name):
        #grab first pose name

        print(f"Grabbing image for Pose: [{pose_name}]")

        expected_file_name = ("_".join(pose_name.lower().split(" ")))+".png"

        # Access the cache
        cache = self.parent().parent().image_cache
            
        # Check cache first
        if expected_file_name in cache:
                return cache[expected_file_name]
            
            # Fallback to no_image if available
        elif "no_image.png" in cache:
                return cache["no_image.png"]
            
        # No image available
        else:
            return None
    
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
            pixmap = self.load_pose_image(current_pose_info["current_pose"]["name"])
            if pixmap is not None:
                scaled_pixmap = pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.active_pose_image.setPixmap(scaled_pixmap)
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
            return

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
            self.pause_button.setVisible(False)
            self.play_button.setVisible(True)
            self.update_view()
        else:
            self.pause_button.setVisible(True)
            self.play_button.setVisible(False)
            self.update_view()