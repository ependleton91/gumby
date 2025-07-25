from PyQt6.QtWidgets import QDialog, QTabWidget,QScrollArea,QLabel,QVBoxLayout,QHBoxLayout,QTextEdit, QDialogButtonBox,QWidget

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
        main_layout = QVBoxLayout()

        # NAME
        name_layout = QHBoxLayout()
        name_label = QLabel("NAME:")
        name_content = QLabel(self.favorite['name'])
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_content)
        main_layout.addLayout(name_layout) 

        #STYLE
        style_layout = QHBoxLayout()
        style_label = QLabel("STYLE:")
        style_content = QLabel(self.favorite['style'])
        style_layout.addWidget(style_label)
        style_layout.addWidget(style_content)
        main_layout.addLayout(style_layout) 

        #CREATED DATE
        created_layout = QHBoxLayout()
        created_label = QLabel("CREATED DATE:")
        created_content = QLabel(self.favorite['created_date'])
        created_layout.addWidget(created_label)
        created_layout.addWidget(created_content)
        main_layout.addLayout(created_layout) 

        # DURATION
        duration_layout = QHBoxLayout()
        duration_label = QLabel("DURATION:")
        duration_content = QLabel(self.favorite['duration'])
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(duration_content)
        main_layout.addLayout(duration_layout) 

        #MUSCLES
        muscles_layout = QHBoxLayout()
        muscles_label = QLabel("MUSCLES TARGETED:")
        muscles_content = QLabel(", ".join(self.favorite['muscles']))
        muscles_layout.addWidget(muscles_label)
        muscles_layout.addWidget(muscles_content)
        main_layout.addLayout(muscles_layout) 

        #DESCRIPTION
        description_layout = QHBoxLayout()
        description_label = QLabel("DESCRIPTION:")
        description_content = QTextEdit(self.favorite['description'])
        description_content.setReadOnly(True)
        description_layout.addWidget(description_label)
        description_layout.addWidget(description_content)
        main_layout.addLayout(description_layout) 




        

        self.setLayout(main_layout)

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
        

        if len(self.favorite["practice_history"]) == 0:
            empty_message = QLabel("No practice sessions for this sequence yet!")
            scroll_layout.addWidget(empty_message)
            print(f"Zero Practice History. Message Displayed: {empty_message}")
        else:
            for session in self.favorite["practice_history"]:
                pass
            
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True) 
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

