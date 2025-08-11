from PyQt6.QtWidgets import QDialog, QLineEdit, QTextEdit, QPushButton, QFormLayout, QLabel, QFileDialog, QScrollArea, QWidget, QVBoxLayout

class pose_details_box(QDialog):
    def __init__(self, pose_info, edit_mode=False):
        super().__init__()
        self.pose_info = pose_info
        self.edit_mode = edit_mode
        
        if edit_mode:
            self.setWindowTitle(f"Edit Pose: {pose_info['name']}")
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
        if not edit_mode:
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
        if edit_mode:
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
        if edit_mode:
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
        if file_path:
            print(f"Selected image: {file_path}")