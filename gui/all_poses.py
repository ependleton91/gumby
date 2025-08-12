from PyQt6.QtWidgets import QMessageBox,QWidget, QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea,QTabWidget, QGridLayout, QFrame,QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from config import POSES_FILE,FLOWS_FILE
from gui.dialogs.pose_details_dialog import pose_details_box
from gui.dialogs.flow_details_dialog import flow_details_box
import json

class PosesWidget(QWidget):
    def __init__(self):
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
        
    def Poses_Tab(self):
        poses_cards_layout = self.create_poses_grid()
        return self.tab_template("POSES",poses_cards_layout)

    def flow_tab(self):
        flow_cards_layout = self.create_flows_list()
        return self.tab_template("FLOWS", flow_cards_layout)

    def tab_template(self,title,cards_layout):
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header section
        button_box = QHBoxLayout()
        header_label = QLabel(title)
        button_box.addWidget(header_label)
        self.add_button = QPushButton("ADD")
        self.add_button.setMaximumWidth(100)
        button_box.addWidget(self.add_button)
        self.add_button.clicked.connect(lambda: self.add_button_clicked())
        
        main_layout.addLayout(button_box)
            

        if title == "POSES":
            self.poses_scroll_area = QScrollArea()
            scroll_area = self.poses_scroll_area
        else:
            scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setLayout(cards_layout)  # Use the passed layout
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        widget.setLayout(main_layout)
        return widget
    
    def  create_flows_list(self):
        flows_list = QVBoxLayout()
        flows_list.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        with open(FLOWS_FILE, 'r') as f:
            flows_data = json.load(f)

        for  flow_key, flow_info in flows_data["flowing_sequences"].items():
            flow_card = self.create_flow_card( flow_info, flow_key)
            flows_list.addWidget(flow_card)

            self.flow_cards[ flow_key] = flow_card


        return flows_list
    
    def create_flow_card(self, flow_info, flow_key):
        card_frame = QFrame()
        card_frame.setObjectName("flowCard")
        card_frame.setFrameStyle(QFrame.Shape.Box)
        card_frame.setFixedSize(600,400) 

        layout = QVBoxLayout()
        card_frame.setLayout(layout)

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
        self.edit_button.clicked.connect(lambda: self.edit_flow( flow_info))

        #Add to layout
        layout.addWidget(flow_name_label)
        layout.addWidget(flow_duration_label) 
        layout.addWidget(flow_category_label)
        layout.addWidget(flow_style_label)
        layout.addWidget(flow_muscles_label)
        layout.addWidget(flow_difficulty_label)
        layout.addWidget(flow_energy_label)
        layout.addWidget(flow_count_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.edit_button)


        # Invisible click button (overlay entire image)
        click_button = QPushButton(card_frame)
        click_button.setGeometry(0, 0, 200, 200) 
        click_button.setStyleSheet("background: transparent; border: none;")
        click_button.clicked.connect(lambda: self.display_flow_deets( flow_info))

        self.edit_button.clicked.connect(lambda: self.edit_flow(flow_info))

        card_frame. flow_key = flow_key

        return card_frame


    def create_poses_grid(self):
        card_grid = QGridLayout()
        card_grid.setSpacing(10)  # Reduce spacing between cards
        card_grid.setContentsMargins(10, 10, 10, 10) 
        
        # Load poses data
        try:
            with open(POSES_FILE, 'r') as f:
                poses_data = json.load(f)
            poses = poses_data.get("poses", {})
        except (FileNotFoundError, json.JSONDecodeError):
            poses = {}  # Handle missing file gracefully
        
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
        card_frame = QFrame()
        card_frame.setObjectName("poseCard")
        card_frame.setFrameStyle(QFrame.Shape.Box)
        card_frame.setFixedSize(350,300)  # Consistent card size

        layout = QVBoxLayout()
        card_frame.setLayout(layout)


        pose_name = pose_info["name"]
        pose_name_label = QLabel(pose_name)
        pose_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        pose_image_widget = QLabel()
        # Create image widget but don't load image yet
        pose_image_widget = QLabel("Loading...")

        pose_image_widget.setFixedSize(275, 190)
        pose_image_widget.pose_name = pose_info["name"] 
        self.pose_image_widgets.append(pose_image_widget)
        pose_image_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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

        card_frame.pose_key = pose_key
        
        
        return card_frame        
  
    def get_pose_image(self, pose_name):
        try:
            cache = self.parent().parent().image_cache
            expected_filename = ("_".join(pose_name.lower().split(" "))) + ".png"
            return cache.get(expected_filename, cache.get("no_image.png"))
        except (AttributeError, TypeError):
            print("Image cache not accessible")
            return None
        
    def load_pose_images(self):
        """Load images for all pose cards when page is accessed"""
        for image_widget in self.pose_image_widgets:
            pose_name = image_widget.pose_name
            pose_image = self.get_pose_image(pose_name)
            
            if pose_image is not None:
                scaled_image = pose_image.scaled(275, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_widget.setPixmap(scaled_image)
            else:
                image_widget.setText("No Image")

    def display_pose_deets(self,pose_info):
        dialog = pose_details_box(pose_info, edit_mode=False,create_mode=False)
        dialog.exec()

    def edit_pose(self, pose_info):
        main_window = self.parent().parent() 
        dialog = pose_details_box(pose_info, edit_mode=True, create_mode=False)
        dialog.image_cache = main_window.image_cache 
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.save_pose_changes(dialog,pose_info)

    def save_pose_changes(self, dialog, original_pose_info):
        # Extract edited data and save to poses.json
        new_data = {}
        new_data["name"]= dialog.name_field.text()
        new_data["description"] = dialog.description_field.toPlainText()
        try:
            new_data["default_duration"] = float(dialog.duration_field.text())
        except:
            print(f"Invalid duration value, keeping original: {original_pose_info['default_duration']}")
        new_data["muscle_groups"] = [muscle.strip() for muscle in dialog.muscles_field.text().split(",")]
        new_data["type"] = dialog.type_field.text()
        new_data["instructions"] = dialog.instructions_field.toPlainText()
        new_data["modifications"] = dialog.modifications_field.toPlainText()
        try: 
            new_data["difficulty"] =  int(dialog.difficulty_field.text())
        except:
            print(f"Invalid difficulty value, keeping original: {original_pose_info['difficulty']}")


        with open(POSES_FILE, 'r') as f:
            poses_data = json.load(f)

        # Single loop to update and capture pose_key
        found_pose_key = None
        for pose_key, pose_data in poses_data["poses"].items():
            if pose_data["name"] == original_pose_info["name"]:
                for key, value in new_data.items():
                    pose_data[key] = value
                found_pose_key = pose_key  # Capture the key
                break

        # Save updated data
        with open(POSES_FILE, 'w') as f:
            json.dump(poses_data, f, indent=2)

        # Update UI card
        if found_pose_key:
            # Get the updated pose data for UI refresh
            updated_pose_data = poses_data["poses"][found_pose_key]
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
        
        # Replace the content in existing scroll area
        self.poses_scroll_area.setWidget(new_scroll_content)
        self.load_pose_images()

    def add_button_clicked(self):
        default_pose_info = {}
        main_window = self.parent().parent()  # Get main window reference
        dialog = pose_details_box(default_pose_info, edit_mode=False, create_mode=True)
        dialog.image_cache = main_window.image_cache  # Pass cache directly
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.add_new_pose(dialog)

    def edit_flow(self, flow_info):
        dialog = flow_details_box(flow_info, edit_mode=True, create_mode=False)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.save_flow_changes(dialog,flow_info)

    def display_flow_deets(self, flow_info):
        dialog = flow_details_box(flow_info, edit_mode=False,create_mode=False)
        dialog.exec()

    def save_flow_changes(self,flow_info):
        
        pass


    def add_new_pose(self,dialog):
        new_data = {}
        
        #Extract data from dialog fields
        #Create pose dictionary structure matching your JSON format
   
        new_data["name"]= dialog.name_field.text()
        #Generate unique pose key from the name (convert to snake_case)
        pose_reference = new_data["name"].lower().replace(" ", "_").strip()
        new_data["description"] = dialog.description_field.toPlainText()
        try:
            new_data["default_duration"] = float(dialog.duration_field.text())
        except:
            print(f"Invalid duration value, keeping default: .5")
            new_data["default_duration"] = float(.5)
        new_data["muscle_groups"] = [muscle.strip() for muscle in dialog.muscles_field.text().split(",")]
        new_data["type"] = dialog.type_field.text()
        new_data["instructions"] = dialog.instructions_field.toPlainText()
        new_data["modifications"] = dialog.modifications_field.toPlainText()
        try: 
            new_data["difficulty"] =  int(dialog.difficulty_field.text())
        except:
            print(f"Invalid difficulty value, keeping default: 2")
            new_data["difficulty"] =  int(2)
        new_data["image_filename"] = dialog.pose_info.get("image_filename", "no_image.png")


        if (new_data["name"] == "Name Your Pose" or 
            new_data["name"].strip() == "" or
            new_data["description"] == "Describe this pose" or
            new_data["description"].strip() == ""):
            
            QMessageBox.warning(self, "Invalid Input", "Please fill out the pose name and description with real values.")
            return

        #Load existing poses JSON
        with open(POSES_FILE, 'r') as f:
            poses_data = json.load(f)

        if pose_reference in poses_data["poses"]:
            QMessageBox.warning(self, "Duplicate Pose", f"A pose with the name '{new_data['name']}' already exists.")
            return

        #Add new pose to the structure
        poses_data["poses"][pose_reference] = new_data

        #Save updated JSON
        with open(POSES_FILE, 'w') as f:
            json.dump(poses_data, f, indent=2)
        
        #Refresh the poses grid to show the new pose
        self.update_pose_grid()