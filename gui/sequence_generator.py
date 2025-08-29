from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QSlider, QComboBox, QCheckBox, 
                            QGroupBox, QGridLayout, QApplication, QDialog, QInputDialog)
from PyQt6.QtCore import Qt
from utils.ui_utils import show_success_message, show_error_message, hide_widgets
from utils.display_utils import format_list_for_display, format_for_internal
from utils.sequence_utils import select_flows_for_sequence, get_available_styles
from utils.database_utils import get_db_manager, create_favorite
from utils.datetime_utils import get_current_timestamp


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
        
        # Muscle groups section
        muscles_group = self.create_muscle_groups_section()
        self.main_layout.addWidget(muscles_group)

        # Store widgets in list
        self.group_of_widgets = [
            self.title,
            duration_group,
            style_group,
            muscles_group
        ]

        # Format widget width
        for widget in self.group_of_widgets:
            widget.setMaximumWidth(sub_widget_width)
        
        # Generate button
        self.generate_btn = QPushButton("Generate My Sequence!")
        self.generate_btn.clicked.connect(self.generate_sequence) 
        self.main_layout.addWidget(self.generate_btn)
        
        # Build layout
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
        
        # Get available styles from database
        try:
            available_styles = get_available_styles()
            display_styles = format_list_for_display(available_styles)
            self.style_dropdown.addItems(display_styles)
        except Exception as e:
            print(f"Error loading styles: {e}")
            # Fallback to basic styles
            self.style_dropdown.addItems(["Vinyasa", "Hatha", "Yin"])

        # Add dropdown to layout
        layout.addWidget(self.style_dropdown)
        group.setLayout(layout)
        return group

    def create_muscle_groups_section(self):
        # Build muscle group checkboxes
        group = QGroupBox("Select Targeted Muscle Groups")
        layout = QGridLayout()

        # Get available muscle groups from database
        try:
            from utils.sequence_utils import extract_unique_values
            from utils.file_utils import load_flows_data
            
            flows_data = load_flows_data()
            available_muscles = extract_unique_values(flows_data, "muscle_groups")
            display_muscles = format_list_for_display(available_muscles)
            
        except Exception as e:
            print(f"Error loading muscle groups: {e}")
            # Fallback to basic muscle groups
            display_muscles = ["Core", "Arms", "Back", "Legs", "Hips", "Full Body"]
        
        self.muscle_checkboxes = []
        for i, muscle in enumerate(display_muscles):
            checkbox = QCheckBox(muscle)
            self.muscle_checkboxes.append(checkbox)  
            # Arrange in grid: 3 columns
            row = i // 3
            col = i % 3
            layout.addWidget(checkbox, row, col)
        
        # Add checkboxes to layout
        group.setLayout(layout)
        return group
    
    def show_results(self, flows):
        """Display generated sequence results."""
        print("Showing results for generated sequence")

        # Hide all option widgets/generate button
        hide_widgets(self.group_of_widgets)
        self.generate_btn.setVisible(False)

        # Initialize results display
        results_title = QLabel("Your Generated Sequence")
        results_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E86AB;")
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Build flow list display
        results_string = ""
        for i, flow in enumerate(flows, 1):
            flow_name = flow.get('name', 'Unknown Flow')
            flow_duration = flow.get('duration', 0)
            results_string += f"{i}. {flow_name} ({flow_duration:.1f} min)\n"
        
        results_list = QLabel(results_string)
        results_list.setWordWrap(True)
        
        # Calculate totals
        total_duration = sum(flow.get('duration', 0) for flow in flows)
        requested_duration = self.duration_slider.value()
        selected_style = self.style_dropdown.currentText()
        
        # Get selected muscles
        selected_muscles = []
        for checkbox in self.muscle_checkboxes:
            if checkbox.isChecked():
                selected_muscles.append(checkbox.text())
        
        # Build result details 
        muscles_text = ", ".join(selected_muscles) if selected_muscles else "All muscle groups"
        results_details = QLabel(
            f"Generated sequence with {len(flows)} flows\n"
            f"Total duration: {total_duration:.1f} minutes (requested: {requested_duration} minutes)\n"
            f"Style: {selected_style}\n"
            f"Target muscle groups: {muscles_text}"
        )
        results_details.setWordWrap(True)
        
        # Build navigation buttons
        refresh_btn = QPushButton("Generate a New Sequence")
        refresh_btn.clicked.connect(self.return_to_main)

        favorite_btn = QPushButton("Save This Sequence")
        favorite_btn.clicked.connect(lambda: self.add_to_favorites(flows))

        # Create list of results widgets
        self.results_widgets = [
            results_title,
            results_list,
            results_details,
            refresh_btn,
            favorite_btn
        ]

        # Make all widgets visible
        for widget in self.results_widgets:
            self.main_layout.addWidget(widget)
    
    def return_to_main(self):
        """Return to the main sequence generation form."""
        print("Returning to main sequence generator")
        
        # Remove results widgets completely
        if hasattr(self, 'results_widgets'):
            for widget in self.results_widgets:
                widget.setVisible(False)
                self.main_layout.removeWidget(widget)
                widget.deleteLater()
            self.results_widgets = []
        
        # Show form widgets
        for widget in self.group_of_widgets:
            widget.setVisible(True)
        self.generate_btn.setVisible(True)

    def add_to_favorites(self, flows):
        """Save the generated sequence to favorites."""
        print("Adding sequence to favorites")

        # Get sequence name from user
        sequence_name, ok = QInputDialog.getText(
            self, 
            'Save Sequence', 
            'Enter a name for this sequence:',
            text=f"{self.style_dropdown.currentText()} Sequence"
        )
        
        if not ok or not sequence_name.strip():
            return

        try:
            # Get selected muscles
            selected_muscles = []
            for checkbox in self.muscle_checkboxes:
                if checkbox.isChecked():
                    selected_muscles.append(format_for_internal(checkbox.text()))

            # Calculate totals
            total_duration = sum(flow.get('duration', 0) for flow in flows)
            style = format_for_internal(self.style_dropdown.currentText())

            # Create favorite data
            favorite_data = {
                "name": sequence_name.strip(),
                "type": "sequence",
                "description": f"Generated {self.style_dropdown.currentText()} sequence",
                "duration": f"{total_duration:.1f} minutes",
                "style": style,
                "muscle_groups": selected_muscles,
                "flows": flows,
                "generated_date": get_current_timestamp(),
                "flow_count": len(flows)
            }

            # Save to database
            if create_favorite(favorite_data):
                show_success_message(self, "Sequence Saved", f"'{sequence_name}' has been saved to your favorites!")
                
                # Navigate to favorites page
                main_window = self.parent().parent()  # Navigate to MainWindow
                if hasattr(main_window, 'favorites_button_was_clicked'):
                    main_window.favorites_button_was_clicked()
                    if hasattr(main_window, 'favorites_widget') and hasattr(main_window.favorites_widget, 'refresh_favorites'):
                        main_window.favorites_widget.refresh_favorites()
            else:
                show_error_message(self, "Save Failed", "Failed to save sequence. Please try again.")

        except Exception as e:
            print(f"Error saving favorite: {e}")
            show_error_message(self, "Save Failed", f"Failed to save sequence: {str(e)}")
        
    def generate_sequence(self):
        """Generate a yoga sequence based on user preferences."""
        print("=== GENERATE SEQUENCE CALLED ===")
        
        # Get user inputs
        style = format_for_internal(self.style_dropdown.currentText())
        duration = self.duration_slider.value()
        
        selected_muscles = []
        for checkbox in self.muscle_checkboxes:
            if checkbox.isChecked():
                selected_muscles.append(format_for_internal(checkbox.text()))
        
        print(f"Style: {style}")
        print(f"Duration: {duration}")
        print(f"Selected muscles: {selected_muscles}")
        
        # Prepare user preferences
        user_preferences = {
            "duration": duration,
            "style": style,
            "muscle_groups": selected_muscles,
            "difficulty": 3  # Default difficulty - could make this user-selectable
        }
        
        try:
            # Generate sequence using database-powered sequence_utils
            flows = select_flows_for_sequence(user_preferences)
            
            if not flows:
                show_error_message(
                    self,
                    "No Flows Found",
                    f"No suitable flows found for {self.style_dropdown.currentText()} style with your criteria. Try selecting different muscle groups or a different style."
                )
                return
            
            print(f"Generated {len(flows)} flows")
            
            # Store the current sequence for potential saving
            self.current_sequence_flows = flows
            
            # Show results
            self.show_results(flows)
            
        except Exception as e:
            print(f"Error generating sequence: {e}")
            import traceback
            traceback.print_exc()
            show_error_message(
                self,
                "Generation Error", 
                "Failed to generate sequence. Please try again.",
                str(e)
            )