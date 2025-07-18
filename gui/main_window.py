
import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout
from services.sequence_generator import SequenceGeneratorWidget
from gui.favorites_page import FavoritesWidget
from gui.all_poses import PosesWidget
from gui.practice_mode import PracticeWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        with open("assets/styles/style.qss", "r") as f:
            style = f.read()
            QApplication.instance().setStyleSheet(style)


        self.main_title = "GUMBY"
        self.setWindowTitle(self.main_title)
        self.showMaximized() 

        # Add All Widgets
        self.sequence_generator = SequenceGeneratorWidget()
        self.favorites_widget = FavoritesWidget()
        self.poses_widget = PosesWidget()
        self.practice_widget = PracticeWidget()

        # Create menu bar
        menubar = self.menuBar()

        # Create "Navigation" menu
        nav_menu = menubar.addMenu("Navigation")

        # Add actions to menu
        home_action = nav_menu.addAction("🏠 Home")
        nav_menu.addSeparator()  # Visual separator line
        generate_action = nav_menu.addAction("⚡ Generate Sequence")
        favorites_action = nav_menu.addAction("❤️ Favorites")
        poses_action = nav_menu.addAction("🧘 All Poses") 
        practice_action = nav_menu.addAction("🎯 Practice Mode")

        # Connect to existing methods
        home_action.triggered.connect(self.back_to_main)
        generate_action.triggered.connect(self.generate_button_was_clicked)
        favorites_action.triggered.connect(self.favorites_button_was_clicked)
        poses_action.triggered.connect(self.poses_button_was_clicked)
        practice_action.triggered.connect(self.practice_button_was_clicked)


        #Button 1 - Generate a sequence
        self.generate_button = QPushButton("Generate a Sequence!")
        self.generate_button.clicked.connect(self.generate_button_was_clicked)

        #Button 2 - Favorite Sequence
        self.favorites_button = QPushButton("View Favorites")
        self.favorites_button.clicked.connect(self.favorites_button_was_clicked)
        #Button 3 - See all poses
        self.poses_button = QPushButton("All Poses!")
        self.poses_button.clicked.connect(self.poses_button_was_clicked)

         #Button 4 - Practice Mode
        self.practice_button = QPushButton("Practice Mode")
        self.practice_button.clicked.connect(self.practice_button_was_clicked)


        self.main_buttons = [
            self.generate_button,
            self.favorites_button, 
            self.poses_button,
            self.practice_button
            ]

        self.all_widgets = [
            self.sequence_generator,
            self.favorites_widget,
            self.poses_widget,
            self.practice_widget
            ] 
    
        for widget in self.all_widgets:
            widget.setVisible(False)

        # build layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        # Add buttons to layout
        layout.addWidget(self.generate_button)
        layout.addWidget(self.favorites_button) 
        layout.addWidget(self.poses_button)
        layout.addWidget(self.practice_button)
        layout.addWidget(self.sequence_generator)
        layout.addWidget(self.practice_widget)
        layout.addWidget(self.favorites_widget)
        layout.addWidget(self.poses_widget)

        # Create container widget and set layout
        container = QWidget()
        container.setLayout(layout)

        # Set as central widget
        self.setCentralWidget(container)
    ####### END OF INIT ##########

    def hide_all_widgets(self):
        for button in self.main_buttons:
            button.setVisible(False)
        for widget in self.all_widgets:
            widget.setVisible(False)

    def show_main_buttons(self):
        for button in self.main_buttons:
            button.setVisible(True) 

    def back_to_main(self):
        self.show_main_page()
    
    def show_main_page(self):
        self.hide_all_widgets()
        self.show_main_buttons()
        self.setWindowTitle(self.main_title)

    def generate_button_was_clicked(self):
        self.setWindowTitle(self.main_title+" - Generate a Sequence")
        self.hide_all_widgets()
        self.sequence_generator.setVisible(True) 
        

    def favorites_button_was_clicked(self):
        self.setWindowTitle(self.main_title+" - Favorites")
        self.hide_all_widgets()
        self.favorites_widget.setVisible(True) 

    def poses_button_was_clicked(self):
        self.setWindowTitle(self.main_title+" - All Poses")
        self.hide_all_widgets()
        self.poses_widget.setVisible(True) 

    def practice_button_was_clicked(self):
        self.setWindowTitle(self.main_title+" - Practice Mode")
        self.hide_all_widgets()
        self.practice_widget.setVisible(True) 