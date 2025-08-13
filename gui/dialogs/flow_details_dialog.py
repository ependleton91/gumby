from PyQt6.QtWidgets import QDialog, QGridLayout,QLineEdit,QFrame,QHBoxLayout,QComboBox, QCheckBox, QGroupBox, QPushButton, QFormLayout, QLabel, QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
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
        self.pose_image_widgets = []
        self.scroll_offset = 0
        
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
        self.name_field.setMinimumWidth(300)  # Make wider
        
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

        self.carousel_container = self.create_pose_carousel()
        main_layout.addWidget(self.carousel_container)

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

    def create_pose_carousel(self):
        """Create the horizontal pose carousel"""
        carousel_widget = QWidget()
        carousel_layout = QHBoxLayout()
        
        # Left arrow
        self.prev_button = QPushButton("←")
        self.prev_button.setFixedSize(50, 50)
        
        # Main pose display area
        self.pose_display = self.create_pose_display()
        
        # Right arrow  
        self.next_button = QPushButton("→")
        self.next_button.setFixedSize(50, 50)
        
        # Add to layout
        carousel_layout.addWidget(self.prev_button)
        carousel_layout.addWidget(self.pose_display)
        carousel_layout.addWidget(self.next_button)

        self.prev_button.clicked.connect(self.scroll_left)
        self.next_button.clicked.connect(self.scroll_right)
        
        carousel_widget.setLayout(carousel_layout)
        return carousel_widget

    def create_pose_display(self):
        display_widget = QWidget()
        display_layout = QVBoxLayout()
        pose_carousel_widget=QWidget()
        pose_carousel_layout = QGridLayout()
        pose_carousel_layout.setSpacing(10)  # Reduce spacing between cards
        pose_carousel_layout.setContentsMargins(10, 10, 10, 10) 
        list_of_pose_cards = self.build_pose_cards_list()
    
        # Calculate which cards to show (sliding window)
        cards_to_show = 5
        start_index = self.scroll_offset
        end_index = min(start_index + cards_to_show, len(list_of_pose_cards))
        
        visible_cards = list_of_pose_cards[start_index:end_index]
        
        # Add visible cards to grid
        for i, card in enumerate(visible_cards):
            pose_carousel_layout.addWidget(card, 1, i)
            
            # Make center card focused (larger/no opacity)
            center_position = len(visible_cards) // 2
            if i == center_position:
                # Apply focused styling
                card.setFixedSize(140, 140)
                card.setStyleSheet("")  # Remove opacity
            else:
                # Apply side card styling  
                card.setFixedSize(100, 100)
                card.setStyleSheet("opacity: 0.6;")

        if len(visible_cards) > 0:
            center_position = len(visible_cards) // 2
            focused_pose_index = start_index + center_position
            
            if focused_pose_index < len(self.flow_info["flow"]):
                focused_pose = self.flow_info["flow"][focused_pose_index]
                self.current_pose_name = QLabel(focused_pose["name"])
                self.current_pose_index = QLabel(f"{focused_pose_index + 1} of {len(self.flow_info['flow'])}")
                self.current_pose_duration = QLabel(f"{focused_pose['duration']} min")

        if self.create_mode or len(self.flow_info["flow"]) == 0:
            self.current_pose_name = QLabel("No poses yet")

        self.current_pose_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_pose_index.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_pose_duration.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pose_carousel_widget.setLayout(pose_carousel_layout)
        display_layout.addWidget(pose_carousel_widget)
        display_layout.addWidget(self.current_pose_name)
        display_layout.addWidget(self.current_pose_index)
        display_layout.addWidget(self.current_pose_duration)
        display_widget.setLayout(display_layout)
        return display_widget

    def build_pose_cards_list(self):
        card_list = []
        dummy_pose = {
            "name": "Add New Pose"
        }
        
        if self.create_mode:
            # Create mode: just show the "+" card
            card_list.append(self.create_pose_card(dummy_pose))
        else:
            # Regular mode: add all poses in the flow
            for pose in self.flow_info["flow"]:
                pose_card = self.create_pose_card(pose)
                card_list.append(pose_card)

        # In edit mode, add the "+" card at the end
        if self.edit_mode:
            card_list.append(self.create_pose_card(dummy_pose))

        return card_list

    def refresh_carousel(self):
        # Remove old carousel
        if self.carousel_container:
            self.layout().removeWidget(self.carousel_container)
            self.carousel_container.deleteLater()
        
        # Create new carousel
        self.carousel_container = self.create_pose_carousel()
        self.layout().insertWidget(-1, self.carousel_container) 

    def create_pose_card(self,pose_info):
        card_frame = QFrame()
        card_frame.setObjectName("poseCard")
        card_frame.setFrameStyle(QFrame.Shape.Box)
        layout = QVBoxLayout() 
        card_frame.setLayout(layout)  
        
        pose_image_widget = QLabel()
        expected_filename = pose_info["name"].lower().replace(" ", "_") + ".png"

        try:
            cache = self.image_cache
            print(f"Cache exists: {cache is not None}")
            print(f"Looking for: {expected_filename}")
            print(f"Cache keys: {list(cache.keys())[:5]}")  # Show first 5 keys
            pose_image = cache.get(expected_filename)
            if pose_image:
                scaled_image = pose_image.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio)
                pose_image_widget.setPixmap(scaled_image)
            else:
                pose_image_widget.setText("No Image")
        except:
            pose_image_widget.setText("Loading...")


        pose_image_widget.pose_name = pose_info["name"] 
        self.pose_image_widgets.append(pose_image_widget)
  

        card_frame.setFixedSize(140, 140)  # Larger
        pose_image_widget.setFixedSize(130, 130)

        
        pose_image_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pose_image_widget)
        return card_frame

    def scroll_left(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self.refresh_carousel()

    def scroll_right(self):
        max_cards = len(self.build_pose_cards_list())
        if self.scroll_offset + 5 < max_cards:  # 5 is cards_to_show
            self.scroll_offset += 1
            self.refresh_carousel()