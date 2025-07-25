from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QComboBox
from PyQt6.QtGui import QPixmap
from gui.sequence_generator import SequenceGeneratorWidget
from config import FAVORITES_FILE, POSES_IMAGE_DIR
import json
import os

class PracticeWidget(QWidget):
    def __init__(self):
        super().__init__() 
        self.current_state = "SELECTION"  # or "PRACTICE" 
        self.selected_favorite = None
        
        # Create both views
        self.selection_view = self.create_selection_view()
        self.practice_view = self.create_practice_view()

        self.cancel_button = QPushButton("Cancel")
        self.select_different_button = QPushButton("Select Different Sequence") 
        self.start_practice_button = QPushButton("Start Practice")
        self.practice_preview = QWidget()

        # Show appropriate view based on state
        layout = QVBoxLayout()
        layout.addWidget(self.selection_view)
        layout.addWidget(self.practice_view)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.select_different_button)
        layout.addWidget(self.start_practice_button)
        layout.addWidget(self.practice_preview)
        self.setLayout(layout)
        self.update_view()

    def update_view(self):
        if self.current_state == "SELECTION":
            self.selection_view.setVisible(True)
            self.practice_view.setVisible(False)
            self.update_buttons_for_selection()
        elif self.current_state == "PRACTICE":
            self.selection_view.setVisible(False) 
            self.practice_view.setVisible(True)
            self.update_buttons_for_practice()

    def load_favorites(self):
        try:
            with open(FAVORITES_FILE, 'r') as f:
                data = json.load(f)
            return data.get("favorites", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []  
        
    def on_favorite_selected(self, favorite):
        self.selected_favorite = favorite
        self.current_state = "PRACTICE"
        self.update_view()
        self.starting_image = self.load_practice_preview(favorite)

    def update_buttons_for_selection(self):
        self.cancel_button.setVisible(True)
        self.select_different_button.setVisible(False)
        self.practice_preview.setVisible(False)
        self.start_practice_button.setVisible(False)

    def update_buttons_for_practice(self):
        self.cancel_button.setVisible(True)
        self.select_different_button.setVisible(True)
        self.practice_preview.setVisible(True)
        self.start_practice_button.setVisible(True)

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
        
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.start_practice_button.clicked.connect(self.start_practice_session)
        self.select_different_button.clicked.connect(self.on_select_different_clicked)

        return practice_widget
    
    def load_practice_preview(self,selected_favorite):
        #grab first pose name
        starting_pose = selected_favorite["sequences"]["warm_up"][0]["flow"][0]["name"]
        print(f"Starting Pose: [{starting_pose}]")

        expected_file_name = ("_".join(starting_pose.lower().split(" ")))+".png"
        full_file_path = POSES_IMAGE_DIR / expected_file_name
        generic_file_path = POSES_IMAGE_DIR / "no_image.png"

        if full_file_path.exists():
            returned_path = full_file_path
            if QPixmap.Load(returned_path).isNull():
                returned_path = generic_file_path
        else:
            returned_path = generic_file_path
        
        loaded_image = QPixmap.Load(returned_path)
        if loaded_image.isNull():
            return None
        else:
            return loaded_image
    
    def on_cancel_clicked(self):
        selection = QMessageBox.question(
            self, 
            "Cancel Session", 
            f"Are you sure you want to cancel this practice session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
            )

        if selection == QMessageBox.StandardButton.Yes:
            self.current_state = "SELECTION"
            self.update_view()
        else:
            return

    def on_select_different_clicked(self):
        self.current_state = "SELECTION"
        self.update_view

    def start_practice_session(self):
        pass
