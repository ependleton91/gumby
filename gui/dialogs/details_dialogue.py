from PyQt6.QtWidgets import QDialog, QMessageBox,QPushButton,QLineEdit,QTabWidget,QScrollArea,QLabel,QVBoxLayout,QHBoxLayout,QTextEdit, QDialogButtonBox,QWidget
from config import FAVORITES_FILE
import json

class details_dialogue_box(QDialog):
        def __init__(self,favorite):
            super().__init__()
            self.favorite = favorite
            tab_widget = QTabWidget()
            tab_widget.addTab(General_Tab(self.favorite),"GENERAL")
            tab_widget.addTab(Sequence_Tab(self.favorite),"SEQUENCE")
            tab_widget.addTab(History_Tab(self.favorite),"HISTORY")


            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)

            button_box.clicked.connect(self.accept)

            main_layout = QVBoxLayout()
            main_layout.addWidget(tab_widget)
            main_layout.addWidget(button_box)
            self.setLayout(main_layout)
            self.setWindowTitle(f"Favorite Details: {self.favorite['name']}")

class General_Tab(QWidget):
    def __init__(self, favorite):
        super().__init__()
        self.favorite = favorite
        self.main_layout = QVBoxLayout()

        # NAME
        self.name_layout = QHBoxLayout()
        name_label = QLabel("NAME:")
        self.name_content = QLabel(self.favorite['name'])
        self.name_layout.addWidget(name_label)
        self.name_layout.addWidget(self.name_content)
        self.main_layout.addLayout(self.name_layout) 

        #STYLE
        style_layout = QHBoxLayout()
        style_label = QLabel("STYLE:")
        style_content = QLabel(self.favorite['style'])
        style_layout.addWidget(style_label)
        style_layout.addWidget(style_content)
        self.main_layout.addLayout(style_layout) 

        #CREATED DATE
        created_layout = QHBoxLayout()
        created_label = QLabel("CREATED DATE:")
        created_content = QLabel(self.favorite['created_date'])
        created_layout.addWidget(created_label)
        created_layout.addWidget(created_content)
        self.main_layout.addLayout(created_layout) 

        # DURATION
        duration_layout = QHBoxLayout()
        duration_label = QLabel("DURATION:")
        duration_content = QLabel(self.favorite['duration'])
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(duration_content)
        self.main_layout.addLayout(duration_layout) 

        #MUSCLES
        muscles_layout = QHBoxLayout()
        muscles_label = QLabel("MUSCLES TARGETED:")
        muscles_content = QLabel(", ".join(self.favorite['muscles']))
        muscles_layout.addWidget(muscles_label)
        muscles_layout.addWidget(muscles_content)
        self.main_layout.addLayout(muscles_layout) 

        #DESCRIPTION
        description_layout = QHBoxLayout()
        description_label = QLabel("DESCRIPTION:")
        self.description_content = QTextEdit(self.favorite['description'])
        self.description_content.setReadOnly(True)
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_content)
        self.main_layout.addLayout(description_layout) 

        
        bottom_content = QWidget()
        bottom_buttons = QHBoxLayout()


        self.edit_mode = False
        self.edit_button = QPushButton("EDIT")
        self.edit_button.setVisible(True)
        self.edit_button.clicked.connect(self.enter_edit_mode)
        bottom_buttons.addWidget(self.edit_button)

        self.save_button = QPushButton("SAVE")
        self.save_button.setVisible(False)
        self.save_button.clicked.connect(self.save_changes)
        bottom_buttons.addWidget(self.save_button)

        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self.cancel_edit)
        bottom_buttons.addWidget(self.cancel_button)

        bottom_content.setLayout(bottom_buttons)

        
        self.main_layout.addWidget(bottom_content)
        self.setLayout(self.main_layout)

    def enter_edit_mode(self):

        self.edit_button.setVisible(False)
        self.save_button.setVisible(True)
        self.cancel_button.setVisible(True)
        self.edit_mode = True
        self.description_content.setReadOnly(False)

        self.original_name = self.favorite['name']
        self.original_description = self.favorite['description']

        self.name_content.setVisible(False)
        self.name_edit=QLineEdit(self.favorite["name"])
        self.name_edit.setReadOnly(False)
        self.name_layout.addWidget(self.name_edit)

    def save_changes(self):
        try:
            with open(FAVORITES_FILE, 'r') as f:
                    favorites_data = json.load(f)

            new_name = self.name_edit.text().strip()
            new_description = self.description_content.toPlainText().strip()

            if len(new_name) == 0:
                QMessageBox.warning(self, "Invalid Name", "Name cannot be empty!")
                return 

            for favorite in favorites_data["favorites"]:
                    if favorite["created_date"] == self.favorite["created_date"]:
                        favorite["name"] = new_name
                        favorite["description"] = new_description
                        break
            
            self.favorite["name"] = new_name
            self.favorite["description"] = new_description
            self.Parent().setWindowTitle(f"Favorite Details: {self.favorite['name']}")

            with open(FAVORITES_FILE, 'w') as f:
                    json.dump(favorites_data, f, indent=2)

            self.exit_edit_mode()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save changes: {str(e)}")
            return

    def cancel_edit(self):
        self.favorite["name"] = self.original_name
        self.favorite["description"] = self.original_description
        
        # Reset edit widgets to original values
        self.name_edit.setText(self.original_name)
        self.description_content.setText(self.original_description)
        self.exit_edit_mode()
        
    def exit_edit_mode(self):

        self.edit_button.setVisible(True)
        self.save_button.setVisible(False)
        self.cancel_button.setVisible(False)
        self.edit_mode = False
        self.description_content.setReadOnly(True)
        self.name_content.setVisible(True)
        self.name_edit.setVisible(False)
        self.name_content.setText(self.favorite["name"]) 

class Sequence_Tab(QWidget):
    def __init__(self, favorite):
        super().__init__()

        self.favorite = favorite
         # map ui title to results title
        section_map = {
            "warm_up":"WARM UP",
            "main_flow":"MAIN FLOW",
            "cool_down":"COOL DOWN"
            }
        main_layout = QVBoxLayout()  # Create layout first
        header_label = QLabel("SEQUENCE DETAILS")
        main_layout.addWidget(header_label)


        counter = 1
        for section_key, sequence_list in favorite['sequences'].items():
        # Create header widget and add it immediately
            section_label = QLabel(f'=== {section_map[section_key]} ===')
            main_layout.addWidget(section_label)
            for sequence in sequence_list:
                # Create sequence widget and add it immediately  
                sequence_text = f'{counter}. {sequence["name"]}'
                sequence_label = QLabel(sequence_text)
                main_layout.addWidget(sequence_label)
                counter += 1

        
        self.setLayout(main_layout)

class History_Tab(QWidget):
    def __init__(self, favorite):
        super().__init__()
        self.favorite = favorite
        main_layout = QVBoxLayout()
        # Create scrollable area for favorites
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        header_label = QLabel("PRACTICE HISTORY")
        main_layout.addWidget(header_label)
        
        practice_history = self.favorite.get("practice_history", [])

        if len(practice_history) == 0:
            empty_message = QLabel("No practice sessions for this sequence yet!")
            scroll_layout.addWidget(empty_message)
            print(f"Zero Practice History. Message Displayed: {empty_message}")
        else:
            for session in self.favorite["practice_history"]:
                card_widget = QWidget()
                card_layout = QVBoxLayout()

                horizontal_widget = QWidget()
                horizontal_layout = QHBoxLayout()

                date_widget=QWidget()
                date_layout = QHBoxLayout()
                date_label = QLabel("DATE:")
                date_content = QLabel(session['date'])
                date_layout.addWidget(date_label)
                date_layout.addWidget(date_content)
                date_widget.setLayout(date_layout)


                rating_widget = QWidget()
                rating_layout = QHBoxLayout()
                rating_label = QLabel("RATING:")
                rating_content = QLabel(str(session['rating']))
                rating_layout.addWidget(rating_label)
                rating_layout.addWidget(rating_content)
                rating_widget.setLayout(rating_layout)
                

                horizontal_layout.addWidget(date_widget)
                horizontal_layout.addWidget(rating_widget)
                horizontal_widget.setLayout(horizontal_layout)

                notes_widget = QWidget()
                notes_layout=QVBoxLayout()
                notes_label = QLabel("NOTES:")
                notes_text = QTextEdit(session["notes"])
                notes_text.setReadOnly(True)
                notes_layout.addWidget(notes_label)
                notes_layout.addWidget(notes_text)
                notes_widget.setLayout(notes_layout)

                
                card_layout.addWidget(horizontal_widget)
                card_layout.addWidget(notes_widget)
                card_widget.setLayout(card_layout)
                scroll_layout.addWidget(card_widget)
            
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True) 
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

