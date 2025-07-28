from PyQt6.QtWidgets import QDialog,QLineEdit,QTextEdit,QPushButton,QFormLayout,QLabel, QMessageBox
from datetime import datetime

class completion_dialog_box(QDialog):
    def __init__(self,practiced_favorite,session_start_time):
        super().__init__()
          # Show completion dialog

        self.name_field = QLineEdit()
        self.name_field.setMinimumWidth(300)
        self.name_field.setReadOnly(True)
        self.duration_field = QLineEdit()
        self.duration_field.setMinimumWidth(300)
        self.name_field.setReadOnly(True)
        self.date_field = QLineEdit()
        self.date_field.setMinimumWidth(300)
        self.name_field.setReadOnly(True)
        self.rating_field = QLineEdit()
        self.rating_field.setMinimumWidth(300)
        self.notes_field = QTextEdit()
        self.notes_field.setMinimumSize(300,100)
        self.save_button = QPushButton("SAVE")
        self.cancel_button=QPushButton("CANCEL")

        layout = QFormLayout()
        layout.addRow("Name:", self.name_field)
        layout.addRow("Practice Date:", self.date_field)
        layout.addRow("Practice Duration:", self.duration_field)
        layout.addRow("Rating:", self.rating_field)
        layout.addRow("Notes:",self.notes_field)

        session_end_time = datetime.now()
        actual_duration = session_end_time - session_start_time
        duration_minutes = actual_duration.total_seconds() / 60
        self.duration_field.setText(f"{duration_minutes:.1f} minutes")

        self.name_field.setText(practiced_favorite["name"])
        self.date_field.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.rating_field.setText("Please enter a number between 1 and 5")
        self.notes_field.setText("Thoughts on this practice? For your own reference!")

        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        



        
