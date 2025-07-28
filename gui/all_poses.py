from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,QTabWidget, QGridLayout, QFrame,QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from config import POSES_FILE
from gui.dialogs.pose_details_dialog import pose_details_box
import json

class PosesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pose_image_widgets = []
        tab_widget = QTabWidget()
        tab_widget.addTab(self.Poses_Tab(),"POSES")
        tab_widget.addTab(self.Sequence_Tab(),"SEQUENCES")

        
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
        self.setWindowTitle(f"TITLE")
        
    def Poses_Tab(self):
        poses_cards_layout = self.create_poses_grid()
        return self.tab_template("POSES",poses_cards_layout)

    def Sequence_Tab(self):
        sequence_cards_layout = self.create_sequences_list()
        return self.tab_template("SEQUENCES",sequence_cards_layout)

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
        
        main_layout.addLayout(button_box)
            
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setLayout(cards_layout)  # Use the passed layout
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        widget.setLayout(main_layout)
        return widget
    
    def create_sequences_list(self):
        sequences_list = QVBoxLayout()
        return sequences_list


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
            
            pose_card = self.create_pose_card(pose_info)
            card_grid.addWidget(pose_card, row, column)
        
        return card_grid
    
    def create_pose_card(self,pose_info):
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
        self.edit_button.clicked.connect(lambda: self.display_pose_deets(pose_info)) 

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
        dialog = pose_details_box(pose_info)
        dialog.exec()
