from PyQt6.QtWidgets import QDialog,QLineEdit,QTextEdit,QPushButton,QFormLayout,QLabel,QFileDialog

class pose_details_box(QDialog):
    def __init__(self, pose_info, edit_mode=False):
        super().__init__()
        self.pose_info = pose_info
        self.edit_mode = edit_mode
        
        if edit_mode:
            self.setWindowTitle(f"Edit Pose: {pose_info['name']}")
        else:
            self.setWindowTitle(f"Pose Details: {pose_info['name']}")

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

        layout = QFormLayout()
        
        # Add upload button only in edit mode
        if edit_mode:
            self.upload_button = QPushButton("Upload New Image")
            self.upload_button.clicked.connect(self.upload_image)
            layout.addRow("Image:", self.upload_button)
        
        layout.addRow("Name: ", self.name_field)
        layout.addRow("Duration: ", self.duration_field)
        layout.addRow("Pose Type: ", self.type_field)
        layout.addRow("Muscles Targeted: ", self.muscles_field)
        layout.addRow("Difficulty Level: ", self.difficulty_field)
        layout.addRow("Description:", self.description_field)
        layout.addRow("Instructions:", self.instructions_field)
        layout.addRow("Modifications:", self.modifications_field)
        
        # Different buttons based on mode
        if edit_mode:
            self.save_button = QPushButton("SAVE")
            self.cancel_button = QPushButton("CANCEL")
            layout.addWidget(self.save_button)
            layout.addWidget(self.cancel_button)
            self.save_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
        else:
            self.ok_button = QPushButton("OK")
            layout.addWidget(self.ok_button)
            self.ok_button.clicked.connect(self.accept)

        self.setLayout(layout)

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