from PyQt6.QtWidgets import QDialog,QLineEdit,QTextEdit,QPushButton,QFormLayout,QLabel

class favorites_dialog_box(QDialog):
    def __init__(self,results,style):
        super().__init__()
        self.results = results
        self.name_field = QLineEdit()
        self.description_field = QTextEdit()
        self.duration_field = QLineEdit()
        self.save_button = QPushButton("SAVE")
        self.cancel_button=QPushButton("CANCEL")

        layout = QFormLayout()
        layout.addRow("Name:", self.name_field)
        layout.addRow("Description:", self.description_field)
        layout.addRow("Duration:", self.duration_field)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)


        self.save_button.clicked.connect(self.accept) #(closes dialog with "accepted" result)
        self.cancel_button.clicked.connect(self.reject) #(closes dialog with "rejected" result)

        self.name_field.setText(f"{style.upper()} {int(results['duration'])} MINUTE FLOW")
        self.description_field.setText(f"{style} class; targets muscles - {', '.join(results['muscles'])}")
        self.duration_field.setText(f"{results['duration']} minutes")
