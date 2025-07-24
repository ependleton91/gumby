from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QSlider, QComboBox, QCheckBox, 
                            QGroupBox, QGridLayout,QApplication,QDialog)
from PyQt6.QtCore import Qt
from services.build_sequence import generate_yoga_class
from gui.dialogs.favorites_dialogue import favorites_dialog_box
import os
import json
import datetime
from config import FAVORITES_FILE


class SequenceGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main layout
        self.main_layout = QVBoxLayout()
        screen = QApplication.primaryScreen()
        screen_width = screen.size().width()
        sub_widget_width = int(screen_width * 0.3)
        
        # Title
        self.title = QLabel("Generate Your Yoga Sequence")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title)
        
        # Duration section
        duration_group = self.create_duration_section()
        self.main_layout.addWidget(duration_group)

        # Style section  
        style_group = self.create_style_section()
        self.main_layout.addWidget(style_group)
        

        #Muscle groups section
        muscles_group = self.create_muscle_groups_section()
        self.main_layout.addWidget(muscles_group)

        #store widgets in list
        self.group_of_widgets = [
            self.title,
            duration_group,
            style_group,
            muscles_group
        ]

        #format widget width
        for widget in self.group_of_widgets:
            widget.setMaximumWidth(sub_widget_width)
        
        # Generate button
        self.generate_btn = QPushButton("Generate My Sequence!")
        self.generate_btn.clicked.connect(self.generate_sequence) 
        self.main_layout.addWidget(self.generate_btn)
        
        #Build layout
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def create_duration_section(self):
        # Create group box for organization
        group = QGroupBox("Class Duration")
        layout = QVBoxLayout()
        
        # Duration slider (15-90 minutes)
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setMinimum(15)
        self.duration_slider.setMaximum(90)
        self.duration_slider.setValue(60)  # Default to 60 minutes
        self.duration_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.duration_slider.setTickInterval(15)  # Ticks every 15 minutes
        
        # Label to show current value
        self.duration_label = QLabel("60 minutes")
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        
        # Connect slider to update label
        self.duration_slider.valueChanged.connect(self.update_duration_label)
        
        # Add to layout
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_slider)
        
        group.setLayout(layout)
        return group

    def update_duration_label(self, value):
        self.duration_label.setText(f"{value} minutes")
    
    def create_style_section(self):
        group = QGroupBox("Yoga Style")
        layout = QVBoxLayout()
    
        # Create dropdown
        self.style_dropdown = QComboBox()
        self.style_dropdown.addItems(["YIN","HATHA","VINYASA"])
        selected_style = self.style_dropdown.currentText()

        #Add dropdown to layout
        layout.addWidget(self.style_dropdown)
        group.setLayout(layout)
        return group

    def create_muscle_groups_section(self):
        #Build muscle group checkboxes
        group = QGroupBox("Select Targeted Muscled Groups")
        layout = QVBoxLayout()

        #add each muscle checkbox to layout
        muscle_groups = ["Abs", "Arms", "Back", "Pelvic Floor","All"]
        self.muscle_checkboxes = []
        for muscle in muscle_groups:
            checkbox = QCheckBox(muscle)
            self.muscle_checkboxes.append(checkbox)  
            layout.addWidget(checkbox)
        
        #store selected muscles
        selected_muscles = []
        for checkbox in self.muscle_checkboxes:
            if checkbox.isChecked():
                selected_muscles.append(checkbox.text())
        
        #add checkboxes to layout
        group.setLayout(layout)
        return group
    
    def show_results(self,results):

        print(f"Printing results")

        #Hide all option widgets/generate button
        for widget in self.group_of_widgets:
            widget.setVisible(False)
        self.generate_btn.setVisible(False)

       #Map section to display name
        section_display_names = {
        "warm_up": "WARM UP",
        "main_flow": "MAIN FLOW", 
        "cool_down": "COOL DOWN"
        }

        #Initialize results text
        results_title = QLabel("Your Generated Sequence")
        results_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E86AB;")
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_string = ""

        #Print sequence and headers with numbers
        counter = 1
        for section_key, sequence_list in results['sequences'].items():
            results_string += f'=== {section_display_names[section_key]} ===\n'
            for sequence in sequence_list:
                results_string += str(counter) + '. ' + sequence['name'] + '\n'
            counter += 1
        results_list = QLabel(results_string)
        
        #Build result details 
        results_details = QLabel(
            f"Here is your sequence for a class that meets the following requirements.... \n"
            f"Total: {results['duration']} minutes, \n"
            f"Targeted Muscle Groups: {results['muscles']}, \n"
            f"Class Type: {self.style_dropdown.currentText()}"
            )
        print(
            f"results sequence = {results_string}"
            f"Here is your sequence for a class that meets the following requirements.... \n"
            f"Total: {results['duration']} minutes, \n"
            f"Targeted Muscle Groups: {results['muscles']}, \n"
            f"Class Type: {self.style_dropdown.currentText()}"
            )
        
        #Build navigation buttons
        refresh_btn = QPushButton("Generate a New Sequence")
        refresh_btn.clicked.connect(self.return_to_main)

        style = self.style_dropdown.currentText()
        favorite_btn= QPushButton("Favorite This Sequence")
        favorite_btn.clicked.connect(lambda: self.add_to_favorites(results, style))

        #Create list of results widgets
        self.results_widgets = [
            results_title,
            results_list,
            results_details,
            refresh_btn,
            favorite_btn
        ]

        #make all widgets visible
        for widget in self.results_widgets:
            self.main_layout.addWidget(widget)
    
    def return_to_main(self):
        # FIRST: Remove results widgets completely
        print(f"Returning to main")
        for widget in self.results_widgets:
            widget.setVisible(False)
            self.main_layout.removeWidget(widget)
            widget.deleteLater()
        self.results_widgets = []
        
        # THEN: Show form widgets
        for widget in self.group_of_widgets:
            widget.setVisible(True)
        self.generate_btn.setVisible(True)

    def add_to_favorites(self,results,style):
        print(f"Add to favorites selected.")

        dialog = favorites_dialog_box(results, style)

        if dialog.exec() == QDialog.DialogCode.Accepted:
        # User clicked Save - get their edited text and save
            name = dialog.name_field.text()
            description = dialog.description_field.toPlainText()
            duration = dialog.duration_field.text()
        # Save to favorites file
            if os.path.exists(FAVORITES_FILE):
                print(f"The path '{FAVORITES_FILE}' exists.")
                with open(FAVORITES_FILE, 'r') as f:
                    favorites_data = json.load(f)
            else:
                print(f"The path '{FAVORITES_FILE}' does not exist.")
                favorites_data = {"favorites": []}

            #initialize favorite json object for current sequence
            new_favorite = {
                "name": name,
                "description": description,
                "duration": duration,
                "sequences": results['sequences'],
                "muscles": results['muscles'], 
                "style": style,
                "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            #Add favorited sequence jObject to favorites
            favorites_data["favorites"].append(new_favorite)
            
            #Write to favorites file
            print("Saving sequence to favorites file")
            with open(FAVORITES_FILE, 'w') as f:
                json.dump(favorites_data, f, indent=2)

    def generate_sequence(self):
        
        class_type = self.style_dropdown.currentText()
        current_duration = current_duration = self.duration_slider.value()
        selected_muscles = [] 
        for checkbox in self.muscle_checkboxes:
            if checkbox.isChecked():
                selected_muscles.append(checkbox.text())
        results = generate_yoga_class(class_type, selected_muscles, current_duration)
        self.show_results(results) 