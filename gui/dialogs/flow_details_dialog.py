from PyQt6.QtWidgets import QDialog, QLineEdit, QComboBox, QCheckBox, QGroupBox, QPushButton, QFormLayout, QLabel, QScrollArea, QWidget, QVBoxLayout
from config import FLOWS_FILE
import json

class flow_details_box(QDialog):
    def __init__(self, flow_info, edit_mode=False, create_mode=False, flow_key=None):
        super().__init__()
        self.flow_info = flow_info
        self.edit_mode = edit_mode
        self.create_mode = create_mode
        self.flow_key = flow_key
        self.muscle_checkboxes = []
        
        self.resize(600, 800)
        
        # Set window title
        if edit_mode:
            self.setWindowTitle(f"Edit Flow: {flow_info['name']}")
        elif create_mode:
            self.setWindowTitle("Add New Flow")
        else:
            self.setWindowTitle(f"Flow Details: {flow_info['name']}")
        
        # Create all fields
        self.create_fields()
        
        # Set read-only status
        self.set_field_modes()
        
        # Create layout
        self.create_layout()
        
        # Populate fields with data
        self.populate_dropdown_options()
        self.populate_fields()
        
    
    def create_fields(self):
        """Create all form fields"""
        self.name_field = QLineEdit()
        self.name_field.setMinimumWidth(400)  # Make wider
        
        self.duration_field = QLineEdit()
        self.duration_field.setMinimumWidth(400)
        
        self.difficulty_field = QLineEdit()
        self.difficulty_field.setMinimumWidth(400)
        
        # Different field types based on mode
        if self.edit_mode or self.create_mode:
            self.style_field = QComboBox()
            self.style_field.setMinimumWidth(400)
            
            self.category_field = QComboBox()
            self.category_field.setMinimumWidth(400)
            
            self.energy_field = QComboBox()
            self.energy_field.setMinimumWidth(400)
            
            self.muscles_field = self.create_muscle_checkboxes()
            self.muscles_field.setMinimumWidth(400)
        else:
            self.style_field = QLineEdit()
            self.style_field.setMinimumWidth(400)
            
            self.category_field = QLineEdit()
            self.category_field.setMinimumWidth(400)
            
            self.energy_field = QLineEdit()
            self.energy_field.setMinimumWidth(400)
            
            self.muscles_field = QLineEdit()
            self.muscles_field.setMinimumWidth(400)
    
    def set_field_modes(self):
        is_editable = self.edit_mode or self.create_mode
        
        self.name_field.setReadOnly(not is_editable)
        self.duration_field.setReadOnly(not is_editable)
        self.difficulty_field.setReadOnly(not is_editable)
        
        if not is_editable:
            self.style_field.setReadOnly(True)
            self.category_field.setReadOnly(True)
            self.energy_field.setReadOnly(True)
            self.muscles_field.setReadOnly(True)
    
    def create_muscle_checkboxes(self):
        """Create muscle group checkboxes for edit/create mode"""
        group_box = QGroupBox("Muscle Groups")
        layout = QVBoxLayout()
        
        # Load unique muscle groups from flows file
        muscle_groups = self.get_unique_muscles()
        
        for muscle in muscle_groups:
            checkbox = QCheckBox(muscle)
            self.muscle_checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        group_box.setLayout(layout)
        return group_box
    
    def get_unique_muscles(self):

        try:
            with open(FLOWS_FILE, 'r') as f:
                flows_data = json.load(f)
            
            all_muscles = set()
            for flow in flows_data["flowing_sequences"].values():
                all_muscles.update(flow["muscle_groups"])
            
            return sorted(list(all_muscles))
        except:
            return ["core", "arms", "legs", "back", "full_body"]  # Fallback
    
    def populate_dropdown_options(self):
        if not (self.edit_mode or self.create_mode):
            return
            
        with open(FLOWS_FILE, 'r') as f:
            flows_data = json.load(f)

        self.all_categories = set()
        self.all_energies = set()
        self.all_styles = set()
        
        for flow in flows_data["flowing_sequences"].values():
            self.all_categories.add(flow["category"])   
            self.all_energies.add(flow["energy_level"])      
            self.all_styles.update(flow["style"])            
        self.style_field.addItems(sorted(list(self.all_styles)))
        self.category_field.addItems(sorted(list(self.all_categories)))
        self.energy_field.addItems(sorted(list(self.all_energies)))
        
    def create_layout(self):
        # Create widget to hold the form

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Add all fields to form
        form_layout.addRow("Name:", self.name_field)
        form_layout.addRow("Duration:", self.duration_field)
        form_layout.addRow("Difficulty:", self.difficulty_field)
        form_layout.addRow("Style:", self.style_field)
        form_layout.addRow("Category:", self.category_field)
        form_layout.addRow("Energy Level:", self.energy_field)
        form_layout.addRow("Muscle Groups:", self.muscles_field)

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
        if self.edit_mode or self.create_mode:
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
        
    def populate_fields(self):
        if self.create_mode:
            self.name_field.setText("Name your flow")
            self.duration_field.setText("Length in minutes")
            self.difficulty_field.setText("1-5")
        else:
            # Populate with actual flow data
            self.name_field.setText(self.flow_info["name"])
            self.duration_field.setText(str(self.flow_info["duration"]))
            self.difficulty_field.setText(str(self.flow_info["difficulty"]))
            
            # Handle style field (different for edit vs view mode)
            if self.edit_mode:
                # Set ComboBox selection
                current_styles = self.flow_info["style"]
                if len(current_styles) > 0:
                    self.style_field.setCurrentText(current_styles[0])  # Set first style
            else:
                # Set LineEdit text
                self.style_field.setText(", ".join(self.flow_info["style"]))
            
            # Handle category field
            if self.edit_mode:
                self.category_field.setCurrentText(self.flow_info["category"])
            else:
                self.category_field.setText(self.flow_info["category"])
            
            # Handle energy field
            if self.edit_mode:
                self.energy_field.setCurrentText(self.flow_info["energy_level"])
            else:
                self.energy_field.setText(self.flow_info["energy_level"])
            
            # Handle muscle groups
            if self.edit_mode:
                # Check appropriate checkboxes
                flow_muscles = self.flow_info["muscle_groups"]
                for checkbox in self.muscle_checkboxes:
                    if checkbox.text() in flow_muscles:
                        checkbox.setChecked(True)
            else:
                self.muscles_field.setText(", ".join(self.flow_info["muscle_groups"]))
