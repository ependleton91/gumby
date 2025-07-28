from PyQt6.QtWidgets import QDialog,QLineEdit,QTextEdit,QPushButton,QFormLayout,QLabel

class pose_details_box(QDialog):
    def __init__(self,pose_info):
        super().__init__()

        self.name_field = QLineEdit()
        self.name_field.setReadOnly(True)
        self.duration_field = QLineEdit()
        self.duration_field.setReadOnly(True)
        self.type_field = QLineEdit()
        self.type_field.setReadOnly(True)
        self.muscles_field = QLineEdit()
        self.muscles_field.setReadOnly(True)
        self.difficulty_field = QLineEdit()
        self.difficulty_field.setReadOnly(True)
        self.description_field = QTextEdit()
        self.description_field.setReadOnly(True)
        self.instructions_field = QTextEdit()
        self.instructions_field.setReadOnly(True)
        self.modifications_field = QTextEdit()
        self.modifications_field.setReadOnly(True)
        self.ok_button = QPushButton("OK")

        layout = QFormLayout()
        layout.addRow("Name: ", self.name_field)
        layout.addRow("Duration: ", self.duration_field)
        layout.addRow("Pose Type: ",self.type_field)
        layout.addRow("Muscles Targeted: ",self.muscles_field)
        layout.addRow("Difficulty Level: ",self.difficulty_field)
        layout.addRow("Description:", self.description_field)
        layout.addRow("Instructions:",self.instructions_field)
        layout.addRow("Modifications:",self.modifications_field)
        layout.addWidget(self.ok_button)


        self.setLayout(layout)


        self.ok_button.clicked.connect(self.accept) #(closes dialog with "accepted" result)

        self.name_field.setText(pose_info["name"])
        self.description_field.setText(pose_info["description"])
        self.duration_field.setText(str(pose_info["default_duration"]))
        self.muscles_field.setText(" , ".join(pose_info["muscle_groups"]))
        self.type_field.setText(pose_info["type"])
        self.instructions_field.setText(pose_info["instructions"])
        self.modifications_field.setText(pose_info["modifications"])
        self.difficulty_field.setText(str(pose_info["difficulty"]))