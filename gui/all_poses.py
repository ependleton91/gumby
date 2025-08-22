from PyQt6.QtWidgets import QMessageBox,QWidget, QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea,QTabWidget, QGridLayout, QFrame,QHBoxLayout
from PyQt6.QtCore import Qt
from gui.dialogs.pose_details_dialog import pose_details_box
from gui.dialogs.flow_details_dialog import flow_details_box
from utils.ui_utils import show_error_message,show_save_success,show_pose_validation_errors
from utils.image_utils import load_pose_image, scale_image_for_display
from utils.validation_utils import validate_new_pose_data,validate_sequence_data,update_flow_durations
from config import POSES_IMAGE_DIR
from utils.file_utils import load_flows_data, load_poses_data,save_poses_data, save_flows_data,update_favorites_after_pose_change, update_favorites_after_flow_change
#The all poses page has two tabs: one for poses and one for flows.
#Each tab has a header with a title and buttons to add new poses or flows.
#The poses tab displays a grid of pose cards, each with an image, name, and edit button.
#The flows tab displays a list of flow cards, each with details like duration, category, style, muscle groups, difficulty, energy level, and a button to edit the flow.
#The poses dialog allows users to view and edit pose details, including name, description, duration, muscle groups, type, instructions, modifications, and difficulty.
#The flows dialog allows users to view and edit flow details, including name, duration, category, style, muscle groups, difficulty, energy level, and the list of poses in the flow.
#The add buttons in each tab open dialogs to create new poses or flows.


class PosesWidget(QWidget):
    def __init__(self):
        # Initialize the base QWidget
        super().__init__()
        self.pose_image_widgets = []
        self.pose_cards = {}
        self.flow_cards={}
        tab_widget = QTabWidget()
        tab_widget.addTab(self.Poses_Tab(),"POSES")
        tab_widget.addTab(self.flow_tab(),"FLOWS")

        
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
        self.setWindowTitle(f"TITLE")
        self.load_pose_images() 

        
    def Poses_Tab(self):
        poses_cards_layout = self.create_poses_grid()
        return self.tab_template("POSES: Click on any pose to see the details. Click edit to update the pose.",poses_cards_layout)

    def flow_tab(self):
        flow_cards_layout = self.create_flows_list()
        return self.tab_template("FLOWS: Click on a flow to see the details. Click edit to update the flow.", flow_cards_layout)

    def tab_template(self,title,cards_layout):
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header section
        button_box = QHBoxLayout()
        header_label = QLabel(title)
        button_box.addWidget(header_label)
        self.add_pose_button = QPushButton("ADD A POSE")
        self.add_pose_button.setMaximumWidth(150)
        button_box.addWidget(self.add_pose_button)
        self.add_pose_button.clicked.connect(lambda: self.add_pose_button_clicked())

        self.add_flow_button = QPushButton("ADD A FLOW")
        self.add_flow_button.setMaximumWidth(150)
        button_box.addWidget(self.add_flow_button)
        self.add_flow_button.clicked.connect(lambda: self.add_flow_button_clicked())
        
        main_layout.addLayout(button_box)
            

        if title == "POSES":
            self.poses_scroll_area = QScrollArea()
            scroll_area = self.poses_scroll_area
        else:
            scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setLayout(cards_layout) 
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        widget.setLayout(main_layout)
        return widget
    
    def  create_flows_list(self):
        flows_list = QVBoxLayout()
        flows_list.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        flows_data = load_flows_data()
        #Add each flow card to the layout
        for  flow_key, flow_info in flows_data["flowing_sequences"].items():
            flow_card = self.create_flow_card( flow_info, flow_key)
            flows_list.addWidget(flow_card)
            self.flow_cards[ flow_key] = flow_card
        return flows_list
    
    # Create a flow card with details like name, duration, category, style, muscle groups, difficulty, energy level, and edit button
    def create_flow_card(self, flow_info, flow_key):
        card_frame = QFrame()
        card_frame.setObjectName("flowCard")
        card_frame.setFrameStyle(QFrame.Shape.Box)
        card_frame.setFixedSize(600,400) 

        layout = QVBoxLayout()
        card_frame.setLayout(layout)
        #Add Name to Card
        flow_name =  flow_info["name"]
        flow_name_label = QLabel(flow_name)
        flow_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Add Duration to Card
        flow_duration =  flow_info["duration"]
        flow_duration_label = QLabel(f"Duration: {flow_duration} minutes")
        flow_duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        #Add Category to Card
        flow_category =  flow_info["category"]
        flow_category_label = QLabel(f"Category: {flow_category}")
        flow_category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Add Styles to Card
        flow_style = flow_info["style"]
        flow_style_label = QLabel(f"Style: {', '.join(flow_style)}") 
        flow_style_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Add Muscle Groups to Card
        flow_muscles = flow_info["muscle_groups"]
        flow_muscles_label = QLabel(f"Muscles: {', '.join(flow_muscles)}")
        flow_muscles_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Add Difficulty to Card
        flow_difficulty =  flow_info["difficulty"]
        flow_difficulty_label = QLabel(f"Difficulty: {flow_difficulty}/5")
        flow_difficulty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Add energy level to Card
        flow_energy =  flow_info["energy_level"]
        flow_energy_label = QLabel(f"Energy: {flow_energy}")
        flow_energy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Add Pose Count to Card
        flow_count_label = QLabel(f"Poses: {len(flow_info['flow'])}")
        flow_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.edit_button = QPushButton("EDIT")
        self.edit_button.setMaximumWidth(100)
        self.edit_button.setStyleSheet("background-color: #a0522d; color: white; font-size: 12px; border-radius: 4px; padding: 4px 8px;")

        #Add to layout
        layout.addWidget(flow_name_label)
        layout.addWidget(flow_duration_label) 
        layout.addWidget(flow_category_label)
        layout.addWidget(flow_style_label)
        layout.addWidget(flow_muscles_label)
        layout.addWidget(flow_difficulty_label)
        layout.addWidget(flow_energy_label)
        layout.addWidget(flow_count_label)
        layout.addWidget(self.edit_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)



        # Invisible click button (overlay entire image)
        click_button = QPushButton(card_frame)
        click_button.setGeometry(0, 0, 600, 350) 
        click_button.setStyleSheet("background: transparent; border: none;")

        # Connect click to display flow details
        click_button.clicked.connect(lambda: self.display_flow_deets(flow_info))
        self.edit_button.clicked.connect(lambda: self.edit_flow(flow_info))

        # Store flow key in the card frame for reference
        card_frame.flow_key = flow_key
        # Add the card frame to the layout
        return card_frame


    def create_poses_grid(self):
        # Create a grid layout for pose cards
        card_grid = QGridLayout()
        card_grid.setSpacing(10)  # Reduce spacing between cards
        card_grid.setContentsMargins(10, 10, 10, 10) 
        
        # Load poses data
        poses_data = load_poses_data()
        poses = poses_data.get("poses", {})
   
        
        # Create cards in 3-column grid
        for index, (pose_key, pose_info) in enumerate(poses.items()):
            row = index // 3
            column = index % 3

            pose_card = self.create_pose_card(pose_info, pose_key)
            card_grid.addWidget(pose_card, row, column)
            # Store the card reference
            self.pose_cards[pose_key] = pose_card
        
        return card_grid
    
    def create_pose_card(self,pose_info,pose_key):
        # Create a card for each pose with its image, name, and edit button
        card_frame = QFrame()
        card_frame.setObjectName("poseCard")
        card_frame.setFrameStyle(QFrame.Shape.Box)
        card_frame.setFixedSize(350,300)

        layout = QVBoxLayout()
        card_frame.setLayout(layout)

        # Add Name to Card
        pose_name = pose_info["name"]
        pose_name_label = QLabel(pose_name)
        pose_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        pose_image_widget = QLabel()
        # Create image widget but don't load image yet
        pose_image_widget = QLabel("Loading...")

        pose_image_widget.setFixedSize(275, 190)
        pose_image_widget.pose_name = pose_info["name"] 
        # Get the pose image from cache
        self.pose_image_widgets.append(pose_image_widget)
        pose_image_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Add edit button to Card
        self.edit_button = QPushButton("EDIT")
        self.edit_button.setMaximumWidth(100)
        self.edit_button.setStyleSheet("background-color: #a0522d; color: white; font-size: 12px; border-radius: 4px; padding: 4px 8px;")
        self.edit_button.clicked.connect(lambda: self.edit_pose(pose_info))

        # Add to layout
        layout.addWidget(pose_image_widget)
        layout.addWidget(pose_name_label)
        layout.addWidget(self.edit_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Invisible click button (overlay entire image)
        click_button = QPushButton(card_frame)
        click_button.setGeometry(0, 0, 200, 200) 
        click_button.setStyleSheet("background: transparent; border: none;")
        click_button.clicked.connect(lambda: self.display_pose_deets(pose_info))
        # Connect edit button to edit pose
        card_frame.pose_key = pose_key
    
        return card_frame        
  
    def get_pose_image(self, pose_name):
        # Attempt to retrieve the pose image from the cache
        return load_pose_image(pose_name, POSES_IMAGE_DIR)

        
    def load_pose_images(self):
        for image_widget in self.pose_image_widgets:
            pose_name = image_widget.pose_name
        
            #load the image from the cache or directory
            pose_image = load_pose_image(pose_name, POSES_IMAGE_DIR)
            #scale the image for display
            scaled_image = scale_image_for_display(pose_image, 275, 250)
            #add the scaled image to the widget
            image_widget.setPixmap(scaled_image)

    def display_pose_deets(self,pose_info):
        # Display pose details in a dialog
        dialog = pose_details_box(pose_info, edit_mode=False,create_mode=False)
        dialog.exec()

    def edit_pose(self, pose_info):
        # Open the pose details dialog in edit mode
        main_window = self.parent().parent() 
        dialog = pose_details_box(pose_info, edit_mode=True, create_mode=False)
        dialog.image_cache = main_window.image_cache 
        result = dialog.exec()

        # If the dialog was accepted, save the changes
        if result == QDialog.DialogCode.Accepted:
            self.save_pose_changes(dialog,pose_info)

    def save_pose_changes(self, dialog, original_pose_info):
        # Extract edited data from dialog
        new_data = {
            "name": dialog.name_field.text(),
            "description": dialog.description_field.toPlainText(),
            "default_duration": dialog.duration_field.text(),
            "muscle_groups": [muscle.strip() for muscle in dialog.muscles_field.text().split(",")],
            "type": dialog.type_field.text(),
            "instructions": dialog.instructions_field.toPlainText(),
            "modifications": dialog.modifications_field.toPlainText(),
            "difficulty": dialog.difficulty_field.text()
        }
        
        # Use comprehensive validation utility
        valid, errors = validate_new_pose_data(new_data)
        if not valid:
            show_pose_validation_errors(self, errors)
            return
        
        # Store original name for flow updates
        original_name = original_pose_info["name"]
        new_name = new_data["name"]
        
        # Update poses data
        poses_data = load_poses_data()
        found_pose_key = None
        for pose_key, pose_data in poses_data["poses"].items():
            if pose_data["name"] == original_name:
                for key, value in new_data.items():
                    pose_data[key] = value
                found_pose_key = pose_key  
                break
        
        # Update flows data if pose name changed
        if original_name != new_name:
            flows_data = load_flows_data()
            updated_flows = False
            
            for flow_id, flow_data in flows_data.get("flowing_sequences", {}).items():
                for pose in flow_data.get("flow", []):
                    if pose.get("name") == original_name:
                        pose["name"] = new_name
                        updated_flows = True
                        print(f"Updated pose name in flow '{flow_data['name']}'")
            
            
            if updated_flows:
                if not save_flows_data(flows_data):
                    show_error_message(self, "Warning", "Pose updated but failed to update some sequences. Some flows may still reference the old pose name.")
                    return
                else:
                    update_flow_durations()

        # Save poses data
        poses_saved = save_poses_data(poses_data)
        if not poses_saved:
            show_error_message(self, "Failed to save pose changes. Please try again.")
            return
        else:
            show_save_success(self, "Pose changes")

        favorites_success = update_favorites_after_pose_change(original_name, new_name, new_data)
        if not favorites_success:
            show_error_message(self, "Warning", "Pose updated but failed to update some favorites.")


        from utils.image_utils import clear_image_cache
        clear_image_cache()

        # Update UI
        if found_pose_key:
            self.update_pose_grid()

    def update_pose_grid(self):
        # Clear pose cards reference
        self.pose_cards = {}
        self.pose_image_widgets = []
        
        # Create new grid
        new_grid = self.create_poses_grid()
        
        # Create new scroll content
        new_scroll_content = QWidget()
        new_scroll_content.setLayout(new_grid)
        
        # Find the poses tab and its scroll area
        tab_widget = self.findChild(QTabWidget)
        if tab_widget:
            poses_tab = tab_widget.widget(0)  # First tab is poses
            if poses_tab:
                scroll_area = poses_tab.findChild(QScrollArea)
                if scroll_area:
                    scroll_area.setWidget(new_scroll_content)
                    self.load_pose_images()
                    return
        
        # Fallback - this shouldn't happen but prevents crashes
        print("Warning: Could not find poses scroll area for update")
    def add_pose_button_clicked(self):
        #Add a new pose dialog
        default_pose_info = {}
        main_window = self.parent().parent()  # Get main window reference
        dialog = pose_details_box(default_pose_info, edit_mode=False, create_mode=True)
        dialog.image_cache = main_window.image_cache  # Pass cache directly
        result = dialog.exec()

        # If the dialog was accepted, add the new pose
        if result == QDialog.DialogCode.Accepted:
            self.add_new_pose(dialog)

    def add_flow_button_clicked(self):
        # Add a new flow dialog
        flow_info = {}
        main_window = self.parent().parent()
        dialog = flow_details_box(flow_info, edit_mode=False, create_mode=True)
        dialog.image_cache = main_window.image_cache  
        result = dialog.exec()
        # If the dialog was accepted, add the new flow
        if result == QDialog.DialogCode.Accepted:
            self.add_new_flow(dialog)

    def edit_flow(self, flow_info):
        # Open the flow details dialog in edit mode
        main_window = self.parent().parent()
        dialog = flow_details_box(flow_info, edit_mode=True, create_mode=False)
        dialog.image_cache = main_window.image_cache  
        result = dialog.exec()

        # If the dialog was accepted, save the changes
        if result == QDialog.DialogCode.Accepted:
            self.save_flow_changes(dialog,flow_info)

    def display_flow_deets(self, flow_info):
        # Display flow details in a dialog
        try:
            dialog = flow_details_box(flow_info, edit_mode=False, create_mode=False)
            dialog.exec()
            
        except Exception as e:
            from utils.ui_utils import show_error_message
            show_error_message(self, "Error", f"Could not open flow details: {str(e)}")
     
    def add_new_pose(self, dialog):
    # Extract data from dialog fields
        new_data = {
            "name": dialog.name_field.text(),
            "description": dialog.description_field.toPlainText(),
            "default_duration": dialog.duration_field.text(),
            "muscle_groups": [muscle.strip() for muscle in dialog.muscles_field.text().split(",")],
            "type": dialog.type_field.text(),
            "instructions": dialog.instructions_field.toPlainText(),
            "modifications": dialog.modifications_field.toPlainText(),
            "difficulty": dialog.difficulty_field.text(),
            "image_filename": dialog.pose_info.get("image_filename", "no_image.png")
        }
        
        # Validate all data at once
        valid, errors = validate_new_pose_data(new_data)
        if not valid:
            show_pose_validation_errors(self, errors)
            return
        
        # Generate unique pose key (using your existing logic)
        from utils.image_utils import standardize_pose_name_to_filename
        pose_reference = standardize_pose_name_to_filename(new_data["name"]).replace(".png", "")
        
        # Load existing poses and check for duplicates
        poses_data = load_poses_data()
        if pose_reference in poses_data["poses"]:
            show_error_message(self, "Duplicate Pose", f"A pose with the name '{new_data['name']}' already exists.")
            return
        
        # Add new pose and save
        poses_data["poses"][pose_reference] = new_data
        
        if save_poses_data(poses_data):
            show_save_success(self, "New pose", new_data["name"])
            self.update_pose_grid()
        else:
            show_error_message(self, "Save Failed", "Failed to save new pose. Please try again.")

    def save_flow_changes(self, dialog, original_flow_info):
        # Extract edited data from dialog
        new_data = {
            "name": dialog.name_field.text(),
            "duration": dialog.duration_field.text(),
            "difficulty": dialog.difficulty_field.text(),
            "category": dialog.category_field.currentText() if hasattr(dialog.category_field, 'currentText') else dialog.category_field.text(),
            "energy_level": dialog.energy_field.currentText() if hasattr(dialog.energy_field, 'currentText') else dialog.energy_field.text(),
        }
        
        # Handle style field (could be ComboBox or text)
        if hasattr(dialog.style_field, 'currentText'):
            new_data["style"] = [dialog.style_field.currentText()]  # Convert to list
        else:
            new_data["style"] = [style.strip() for style in dialog.style_field.text().split(",")]
        
        # Handle muscle groups (checkboxes or text)
        if hasattr(dialog, 'muscle_checkboxes'):
            new_data["muscle_groups"] = [cb.text() for cb in dialog.muscle_checkboxes if cb.isChecked()]
        else:
            new_data["muscle_groups"] = [muscle.strip() for muscle in dialog.muscles_field.text().split(",")]
        
        # ✨ NEW: Get updated flow/poses from the dialog
        new_data["flow"] = dialog.flow_info.get("flow", [])  # This contains the updated poses
        new_data["tags"] = original_flow_info.get("tags", [])  # Keep existing tags
        
        # Validate the data
        valid, error = validate_sequence_data(new_data)
        if not valid:
            show_pose_validation_errors(self, [error])
            return
        
        # Convert data types
        try:
            new_data["duration"] = float(new_data["duration"])/60
            new_data["difficulty"] = int(new_data["difficulty"])
        except ValueError:
            show_error_message(self, "Invalid Input", "Duration must be a number and difficulty must be 1-5.")
            return
        
        # Recalculate total duration based on poses
        if new_data["flow"]:
            calculated_duration = sum(pose.get("duration", 30)/60 for pose in new_data["flow"])
            new_data["duration"] = round(calculated_duration, 2)
        
        # Load flows data and find the flow to update
        flows_data = load_flows_data()
        original_name = original_flow_info["name"]
        found_flow_key = None
        
        for flow_key, flow_data in flows_data.get("flowing_sequences", {}).items():
            if flow_data["name"] == original_name:
                # Update all fields including the updated poses
                for key, value in new_data.items():
                    flow_data[key] = value
                found_flow_key = flow_key
                break
        
        if not found_flow_key:
            show_error_message(self, "Error", "Could not find flow to update.")
            return
        
        # Save updated flows data
        if save_flows_data(flows_data):
            show_save_success(self, "Flow changes", new_data["name"])
            self.update_flows_list()

            favorites_success = update_favorites_after_flow_change(original_name, new_data)
            if not favorites_success:
                show_error_message(self, "Warning", "Flow updated but failed to update some favorites.")
     
        else:
            show_error_message(self, "Save Failed", "Failed to save flow changes. Please try again.")

    def add_new_flow(self, dialog):
        # Extract data from dialog fields
        new_data = {
            "name": dialog.name_field.text(),
            "duration": dialog.duration_field.text(),
            "difficulty": dialog.difficulty_field.text(),
            "category": dialog.category_field.currentText() if hasattr(dialog.category_field, 'currentText') else dialog.category_field.text(),
            "energy_level": dialog.energy_field.currentText() if hasattr(dialog.energy_field, 'currentText') else dialog.energy_field.text(),
            "flow": dialog.flow_info.get("flow", []),  # ✨ Get poses from dialog
            "tags": []
        }
        
        # Handle style field
        if hasattr(dialog.style_field, 'currentText'):
            new_data["style"] = [dialog.style_field.currentText()]
        else:
            new_data["style"] = [style.strip() for style in dialog.style_field.text().split(",")]
        
        # Handle muscle groups
        if hasattr(dialog, 'muscle_checkboxes'):
            new_data["muscle_groups"] = [cb.text() for cb in dialog.muscle_checkboxes if cb.isChecked()]
        else:
            new_data["muscle_groups"] = [muscle.strip() for muscle in dialog.muscles_field.text().split(",")]
        
        # Check for placeholder text
        if (new_data["name"] == "Name your flow" or 
            new_data["name"].strip() == ""):
            show_error_message(self, "Invalid Input", "Please enter a real flow name.")
            return
        
        # Validate the data
        valid, error = validate_sequence_data(new_data)
        if not valid:
            show_pose_validation_errors(self, [error])  # ← Wrap in list
            return
        
        # Convert data types and calculate duration
        try:
            new_data["difficulty"] = int(new_data["difficulty"])
            
            # Calculate duration from poses if poses exist
            if new_data["flow"]:
                calculated_duration = sum(pose.get("duration", 0.5) for pose in new_data["flow"])
                new_data["duration"] = round(calculated_duration, 2)
            else:
                new_data["duration"] = float(new_data["duration"]) if new_data["duration"] else 1.0
                
        except ValueError:
            show_error_message(self, "Invalid Input", "Difficulty must be 1-5.")
            return
        
        # Generate unique flow key
        flow_reference = new_data["name"].lower().replace(" ", "_").replace("'", "").strip()
        
        # Load existing flows and check for duplicates
        flows_data = load_flows_data()
        if flow_reference in flows_data.get("flowing_sequences", {}):
            show_error_message(self, "Duplicate Flow", f"A flow with the name '{new_data['name']}' already exists.")
            return
        
        # Add new flow to the structure
        if "flowing_sequences" not in flows_data:
            flows_data["flowing_sequences"] = {}
        flows_data["flowing_sequences"][flow_reference] = new_data
        
        # Save updated flows data
        if save_flows_data(flows_data):
            show_save_success(self, "New flow", new_data["name"])
            self.update_flows_list()
        else:
            show_error_message(self, "Save Failed", "Failed to save new flow. Please try again.")

    def update_flows_list(self):
        """Refresh the flows list display after changes"""
        # Clear existing flow cards reference
        self.flow_cards = {}
        
        # Find the flows tab widget and get its scroll area
        # You have a tabbed interface, so we need to update the flows tab content
        tab_widget = self.findChild(QTabWidget)
        if tab_widget:
            # Find the flows tab (index 1 based on your tab_widget.addTab calls)
            flows_tab = tab_widget.widget(1)  # Second tab is flows
            if flows_tab:
                # Get the scroll area from the flows tab
                scroll_area = flows_tab.findChild(QScrollArea)
                if scroll_area:
                    # Create new flows layout
                    new_flows_layout = self.create_flows_list()
                    new_scroll_content = QWidget()
                    new_scroll_content.setLayout(new_flows_layout)
                    scroll_area.setWidget(new_scroll_content)