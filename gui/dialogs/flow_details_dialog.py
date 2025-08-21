from PyQt6.QtWidgets import QDialog, QGridLayout,QListWidget,QLineEdit,QHBoxLayout,QComboBox, QCheckBox, QGroupBox, QPushButton, QFormLayout, QLabel, QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from utils.file_utils import load_flows_data,load_poses_data
from utils.datetime_utils import format_duration_minutes

class flow_details_box(QDialog):
    def __init__(self, flow_info, edit_mode=False, create_mode=False, flow_key=None, image_cache=None):
        super().__init__()
        self.flow_info = flow_info
        self.edit_mode = edit_mode
        self.create_mode = create_mode
        self.flow_key = flow_key
        self.image_cache = image_cache  # Set cache BEFORE creating UI
        self.muscle_checkboxes = []
        self.scroll_offset = 0
        
        self.resize(800,800)
        
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
        self.name_field.setMinimumWidth(300)
        
        self.duration_field = QLineEdit()
        self.duration_field.setMinimumWidth(300)
        
        self.difficulty_field = QLineEdit()
        self.difficulty_field.setMinimumWidth(300)
        
        # Different field types based on mode
        if self.edit_mode or self.create_mode:
            self.style_field = QComboBox()
            self.style_field.setMinimumWidth(300)
            
            self.category_field = QComboBox()
            self.category_field.setMinimumWidth(300)
            
            self.energy_field = QComboBox()
            self.energy_field.setMinimumWidth(300)
            
            self.muscles_field = self.create_muscle_checkboxes()
            self.muscles_field.setMinimumWidth(300)
        else:
            self.style_field = QLineEdit()
            self.style_field.setMinimumWidth(300)
            
            self.category_field = QLineEdit()
            self.category_field.setMinimumWidth(300)
            
            self.energy_field = QLineEdit()
            self.energy_field.setMinimumWidth(300)
            
            self.muscles_field = QLineEdit()
            self.muscles_field.setMinimumWidth(300)
    
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
        group_box = QGroupBox("Muscle Groups")
        
        # Use QGridLayout instead of QVBoxLayout for 4-column grid
        layout = QGridLayout()
        layout.setSpacing(5)  # Tighter spacing
        
        # Load unique muscle groups from flows file
        muscle_groups = self.get_unique_muscles()
        
        # Calculate grid positions for 4 columns
        for index, muscle in enumerate(muscle_groups):
            row = index // 4  # Integer division for row
            column = index % 4  # Remainder for column
            
            checkbox = QCheckBox(muscle)
            self.muscle_checkboxes.append(checkbox)
            layout.addWidget(checkbox, row, column)
        
        group_box.setLayout(layout)
        return group_box
        
    def get_unique_muscles(self):
        try:
            flows_data = load_flows_data()
            
            all_muscles = set()
            for flow in flows_data["flowing_sequences"].values():
                all_muscles.update(flow["muscle_groups"])
            
            return sorted(list(all_muscles))
        except:
            return ["core", "arms", "legs", "back", "full_body"]  # Fallback
    
    def populate_dropdown_options(self):
        if not (self.edit_mode or self.create_mode):
            return
            
        flows_data = load_flows_data()

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
        
        # ADD POSE DISPLAY SECTION:
        pose_display = self.create_pose_display()
        
        # Create main content widget that holds both form and poses
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.addWidget(form_widget)
        content_layout.addWidget(pose_display)  # ← Add poses section
        content_widget.setLayout(content_layout)
        
        # Create scroll area and add the content widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)  
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
            self.duration_field.setText(format_duration_minutes((self.flow_info["duration"])))
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

    def sync_poses_to_data(self):
        #all it before saving to ensure everything is synced
        
        if not hasattr(self, 'poses_list'):
            return  # No editable list (view mode)
        
        # Optional: Validate that list matches data
        if "flow" in self.flow_info:
            if len(self.flow_info["flow"]) != self.poses_list.count():

                print("Warning: Poses list and data are out of sync!")
    def accept(self):
        """Override accept to sync data before closing"""
        if self.edit_mode or self.create_mode:
            self.sync_poses_to_data()
        super().accept()

    def create_pose_display(self):
        """Create editable pose list with add/delete/reorder functionality"""
        display_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        poses_label = QLabel("Poses in this Flow:")
        poses_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        poses_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(poses_label)
        
        # Editable list widget
        self.poses_list = QListWidget()
        self.poses_list.setMinimumHeight(300)
        self.poses_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)  # Enable drag-drop reordering
        
        # Populate list
        self.populate_poses_list()
        
        # Buttons for editing (only show in edit/create mode)
        if self.edit_mode or self.create_mode:
            buttons_layout = QHBoxLayout()
            
            self.add_pose_btn = QPushButton("Add Pose")
            self.remove_pose_btn = QPushButton("Delete")
            self.move_up_btn = QPushButton("Move Up")
            self.move_down_btn = QPushButton("Move Down")
            
            buttons_layout.addWidget(self.add_pose_btn)
            buttons_layout.addWidget(self.remove_pose_btn)
            buttons_layout.addWidget(self.move_up_btn)
            buttons_layout.addWidget(self.move_down_btn)
            
            # Connect button actions
            self.add_pose_btn.clicked.connect(self.add_pose_to_flow)
            self.remove_pose_btn.clicked.connect(self.remove_pose_from_flow)
            self.move_up_btn.clicked.connect(self.move_pose_up)
            self.move_down_btn.clicked.connect(self.move_pose_down)
            
            layout.addWidget(buttons_layout_widget := QWidget())
            buttons_layout_widget.setLayout(buttons_layout)
        
        layout.addWidget(self.poses_list)
        display_widget.setLayout(layout)
        return display_widget

    def populate_poses_list(self):
        """Fill the list with current poses"""
        if not hasattr(self, 'poses_list'):
            return
            
        self.poses_list.clear()
        
        # Initialize flow if it doesn't exist (for create mode)
        if "flow" not in self.flow_info:
            self.flow_info["flow"] = []
        
        # Only add placeholder if there are NO poses
        if not self.flow_info["flow"]:  # If flow list is empty
            self.poses_list.addItem("No poses yet - click 'Add Pose' to start")
        else:
            # Add actual poses
            for i, pose in enumerate(self.flow_info["flow"]):
                duration_text = format_duration_minutes(pose.get("duration", 0.5))
                list_item = f"{pose['name']} ({duration_text})"
                self.poses_list.addItem(list_item)
        
        if not self.create_mode and "flow" in self.flow_info:
            for i, pose in enumerate(self.flow_info["flow"]):
                duration_text = f"{pose.get('duration', 0.5)} min"
                list_item = f"{pose['name']} ({duration_text})"
                self.poses_list.addItem(list_item)
        
        if self.poses_list.count() == 0:
            self.poses_list.addItem("No poses yet - click 'Add Pose' to start")

    def add_pose_to_flow(self):
        """Add a new pose to the flow"""
        from PyQt6.QtWidgets import QInputDialog
        
        # Get available poses
        poses_data = load_poses_data()
        available_poses = list(poses_data.get("poses", {}).keys())
        
        if not available_poses:
            from utils.ui_utils import show_error_message
            show_error_message(self, "No Poses Available", "No poses found. Please add some poses first.")
            return
            
        pose_names = [poses_data["poses"][key]["name"] for key in available_poses]
        
        # Let user select a pose
        pose_name, ok = QInputDialog.getItem(
            self, "Add Pose", "Select a pose to add:", pose_names, 0, False
        )
        
        if ok and pose_name:
            # Get default duration
            duration, ok = QInputDialog.getDouble(
                self, "Pose Duration", f"Duration for {pose_name} (minutes):", 0.5, 0.1, 10.0, 1
            )
            
            if ok:
                # Initialize flow if needed
                if "flow" not in self.flow_info:
                    self.flow_info["flow"] = []
                
                # Remove placeholder if this is the first real pose
                if (self.poses_list.count() == 1 and 
                    self.poses_list.item(0) and 
                    "No poses yet" in self.poses_list.item(0).text()):
                    self.poses_list.clear()
                
                # Add to the list display
                list_item = f"{pose_name} ({duration} min)"
                self.poses_list.addItem(list_item)
                
                # Add to flow_info data
                self.flow_info["flow"].append({
                    "name": pose_name,
                    "duration": duration,
                    "type": "main"
                })
    def remove_pose_from_flow(self):
        """Remove selected pose from flow"""
        current_row = self.poses_list.currentRow()
        if current_row >= 0:
            # Remove from display
            self.poses_list.takeItem(current_row)
            
            # Remove from flow_info data
            if "flow" in self.flow_info and current_row < len(self.flow_info["flow"]):
                del self.flow_info["flow"][current_row]
            
            # If no poses left, add placeholder
            if not self.flow_info.get("flow", []):
                self.poses_list.addItem("No poses yet - click 'Add Pose' to start")

    def move_pose_up(self):
        """Move selected pose up in the list"""
        current_row = self.poses_list.currentRow()
        if current_row > 0:
            # Move in display
            item = self.poses_list.takeItem(current_row)
            self.poses_list.insertItem(current_row - 1, item)
            self.poses_list.setCurrentRow(current_row - 1)
            
            # Move in flow_info data
            if "flow" in self.flow_info:
                self.flow_info["flow"][current_row], self.flow_info["flow"][current_row - 1] = \
                    self.flow_info["flow"][current_row - 1], self.flow_info["flow"][current_row]

    def move_pose_down(self):
        """Move selected pose down in the list"""
        current_row = self.poses_list.currentRow()
        if current_row >= 0 and current_row < self.poses_list.count() - 1:
            # Move in display
            item = self.poses_list.takeItem(current_row)
            self.poses_list.insertItem(current_row + 1, item)
            self.poses_list.setCurrentRow(current_row + 1)
            
            # Move in flow_info data
            if "flow" in self.flow_info:
                self.flow_info["flow"][current_row], self.flow_info["flow"][current_row + 1] = \
                    self.flow_info["flow"][current_row + 1], self.flow_info["flow"][current_row]