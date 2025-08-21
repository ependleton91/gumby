from PyQt6.QtWidgets import QDialog, QLineEdit, QTextEdit, QPushButton, QFormLayout, QLabel, QFileDialog, QScrollArea, QWidget, QVBoxLayout
from PIL import Image 
from utils.ui_utils import show_error_message
from utils.image_utils import standardize_pose_name_to_filename, validate_image_file, create_placeholder_image, load_image_from_path
from config import POSES_IMAGE_DIR 
from PyQt6.QtGui import QPixmap


class pose_details_box(QDialog):
    def __init__(self, pose_info, edit_mode=False, create_mode = False):
        super().__init__()
        self.pose_info = pose_info
        self.edit_mode = edit_mode
        self.create_mode = create_mode
        
        if edit_mode:
            self.setWindowTitle(f"Edit Pose: {pose_info['name']}")
        elif create_mode:
            self.setWindowTitle(f"Add New Pose")
        else:
            self.setWindowTitle(f"Pose Details: {pose_info['name']}")

        # Set dialog size
        self.resize(600, 800)

        self.name_field = QLineEdit()
        self.duration_field = QLineEdit()
        self.type_field = QLineEdit()
        self.muscles_field = QLineEdit()
        self.difficulty_field = QLineEdit()
        self.description_field = QTextEdit()
        self.instructions_field = QTextEdit()
        self.modifications_field = QTextEdit()
        
        # Set read-only based on mode
        if not edit_mode and not create_mode:
            self.name_field.setReadOnly(True)
            self.duration_field.setReadOnly(True)
            self.type_field.setReadOnly(True)
            self.muscles_field.setReadOnly(True)
            self.difficulty_field.setReadOnly(True)
            self.description_field.setReadOnly(True)
            self.instructions_field.setReadOnly(True)
            self.modifications_field.setReadOnly(True)

        # Create the form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)  # Add more spacing between rows
        
        # Add upload button only in edit mode
        if edit_mode or create_mode:
            self.upload_button = QPushButton("Upload New Image")
            self.upload_button.clicked.connect(self.upload_image)
            form_layout.addRow("Image:", self.upload_button)
        
        form_layout.addRow("Name: ", self.name_field)
        form_layout.addRow("Duration: ", self.duration_field)
        form_layout.addRow("Pose Type: ", self.type_field)
        form_layout.addRow("Muscles Targeted: ", self.muscles_field)
        form_layout.addRow("Difficulty Level: ", self.difficulty_field)
        form_layout.addRow("Description:", self.description_field)
        form_layout.addRow("Instructions:", self.instructions_field)
        form_layout.addRow("Modifications:", self.modifications_field)
        
        # Create widget to hold the form
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        
        # Create scroll area and add the form widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(form_widget)
        scroll_area.setWidgetResizable(True)
        
        # Create main layout for the dialog
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        
        # Add buttons below the scroll area
        if edit_mode or create_mode:
            self.save_button = QPushButton("SAVE")
            self.cancel_button = QPushButton("CANCEL")
            main_layout.addWidget(self.save_button)
            main_layout.addWidget(self.cancel_button)
            self.save_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
        else:
            self.ok_button = QPushButton("OK")
            main_layout.addWidget(self.ok_button)
            self.ok_button.clicked.connect(self.accept)

        self.setLayout(main_layout)

        # Populate fields
        if create_mode:
            self.name_field.setText("Name Your Pose")
            self.description_field.setText("Describe this pose")
            self.duration_field.setText(str(.5))
            self.muscles_field.setText("i.e. abs, hamstrings")
            self.type_field.setText("main, transition, set-up, preparation,rest")
            self.instructions_field.setText("How to enter this pose")
            self.modifications_field.setText("Optional: alternate forms of this pose")
            self.difficulty_field.setText("1-5")
        else:
            self.name_field.setText(pose_info["name"])
            self.description_field.setText(pose_info["description"])
            self.duration_field.setText(str(pose_info["default_duration"]))
            self.muscles_field.setText(" , ".join(pose_info["muscle_groups"]))
            self.type_field.setText(pose_info["type"])
            self.instructions_field.setText(pose_info["instructions"])
            self.modifications_field.setText(pose_info["modifications"])
            self.difficulty_field.setText(str(pose_info["difficulty"]))

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
        self, "Select Pose Image", 
        "", "Image Files (*.png *.jpg *.jpeg)"
        )
    
        if not file_path:  # User cancelled
            return
            
        # Validate the image FIRST (before doing anything else)
        if not validate_image_file(file_path):
            show_error_message(self, "Invalid Image", "Please select a valid image file.")
            return

        # Generate filename and path
        new_filename = standardize_pose_name_to_filename(self.name_field.text())
        new_filepath = POSES_IMAGE_DIR / new_filename
        
        try:
            # Convert and save image
            image = Image.open(file_path)
            image.save(new_filepath, "PNG")
            self.pose_info["image_filename"] = new_filename

            # Refresh cache properly
            from utils.image_utils import clear_image_cache
            clear_image_cache()  # Clear entire cache to ensure consistency

            
            print(f"Successfully saved image: {new_filename}")
            
        except Exception as e:
            show_error_message(self, "Upload Failed", f"Failed to save image: {str(e)}")