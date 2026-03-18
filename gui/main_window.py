import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout
from gui.sequence_generator import SequenceGeneratorWidget
from gui.favorites_page import FavoritesWidget
from gui.all_poses import PosesWidget
from gui.practice_mode import PracticeWidget
from config import POSES_IMAGE_DIR
from utils.image_utils import preload_common_poses, get_cache_stats, clear_image_cache
from utils.database_utils import get_db_manager, get_all_poses
from utils.ui_utils import show_error_message, show_success_message
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize database first
        self.initialize_database()

        # Read qss style sheet
        try:
            with open("assets/styles/style.qss", "r") as f:
                style = f.read()
                QApplication.instance().setStyleSheet(style)
        except FileNotFoundError:
            logger.warning("Style sheet not found, using default styling")

        # Generate site title
        self.main_title = "GUMBY"
        self.setWindowTitle(self.main_title)
        self.showMaximized() 

        # Initialize optimized image cache
        self.initialize_image_cache()

        # Add All Widgets
        self.sequence_generator = SequenceGeneratorWidget()
        self.favorites_widget = FavoritesWidget()
        self.poses_widget = PosesWidget()
        self.practice_widget = PracticeWidget()

        # Create menu bar
        self.setup_menu_bar()

        # Create main buttons
        self.setup_main_buttons()

        # Build layout
        self.setup_layout()

    def initialize_database(self):
        """Initialize database connection and handle any errors."""
        try:
            db = get_db_manager()
            logger.info("Database initialized successfully")
            
            # Test basic functionality
            poses_count = len(get_all_poses())
            logger.info(f"Database contains {poses_count} poses")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # You might want to show an error dialog here
            # For now, we'll continue but the app may have limited functionality

    def initialize_image_cache(self):
        """Initialize optimized image caching using the new image utils."""
        try:
            # Get common pose names from database for preloading
            poses = get_all_poses()
            if poses:
                # Preload the first 50 most common poses
                common_pose_names = [pose['name'] for pose in poses[:50]]
                preload_common_poses(common_pose_names, POSES_IMAGE_DIR)
                logger.info(f"Started preloading {len(common_pose_names)} common pose images")
            
            # Log cache stats
            stats = get_cache_stats()
            logger.info(f"Image cache initialized: {stats}")
            
        except Exception as e:
            logger.error(f"Image cache initialization failed: {e}")

    def setup_menu_bar(self):
        """Create and configure the menu bar."""
        menubar = self.menuBar()

        # Create "Navigation" menu
        nav_menu = menubar.addMenu("Navigation")

        # Add actions to menu
        home_action = nav_menu.addAction("🏠 Home")
        nav_menu.addSeparator()  # Visual separator line
        generate_action = nav_menu.addAction("⚡ Generate Sequence")
        sequences_action = nav_menu.addAction("📋 My Sequences")  # Updated from favorites
        poses_action = nav_menu.addAction("🧘 All Poses + Flows") 
        practice_action = nav_menu.addAction("🎯 Practice Mode")
        
        # Add utility menu
        nav_menu.addSeparator()
        cache_action = nav_menu.addAction("🔧 Clear Cache")
        stats_action = nav_menu.addAction("📊 Cache Stats")

        # Connect to click methods
        home_action.triggered.connect(self.back_to_main)
        generate_action.triggered.connect(self.generate_button_was_clicked)
        sequences_action.triggered.connect(self.sequences_button_was_clicked)  # Updated
        poses_action.triggered.connect(self.poses_button_was_clicked)
        practice_action.triggered.connect(self.practice_button_was_clicked)
        cache_action.triggered.connect(self.clear_all_caches)
        stats_action.triggered.connect(self.show_cache_stats)

    def setup_main_buttons(self):
        """Create and configure main navigation buttons."""
        # Button 1 - Generate a sequence
        self.generate_button = QPushButton("Generate a New Sequence")
        self.generate_button.clicked.connect(self.generate_button_was_clicked)

        # Button 2 - My Sequences (updated from favorites)
        self.sequences_button = QPushButton("My Sequences")
        self.sequences_button.clicked.connect(self.sequences_button_was_clicked)
        
        # Button 3 - See all poses
        self.poses_button = QPushButton("Poses + Flows")
        self.poses_button.clicked.connect(self.poses_button_was_clicked)

        # Button 4 - Practice Mode
        self.practice_button = QPushButton("Practice Mode")
        self.practice_button.clicked.connect(self.practice_button_was_clicked)

        # Build list of buttons 
        self.main_buttons = [
            self.generate_button,
            self.sequences_button,  # Updated
            self.poses_button,
            self.practice_button
        ]

        # Style the main buttons
        for button in self.main_buttons:
            button.setMinimumHeight(60)
            button.setMaximumWidth(300)

    def setup_layout(self):
        """Setup the main window layout."""
        # Build list of widgets for main window
        self.all_widgets = [
            self.sequence_generator,
            self.favorites_widget,  # Keep for backward compatibility
            self.poses_widget,
            self.practice_widget
        ] 

        # Set all main window widgets invisible initially
        for widget in self.all_widgets:
            widget.setVisible(False)

        # Build layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)  # Add spacing between buttons

        # Add title area
        title_label = QWidget()
        title_label.setFixedHeight(50)  # Space for title area

        # Add buttons to layout
        layout.addWidget(title_label)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.sequences_button)
        layout.addWidget(self.poses_button)
        layout.addWidget(self.practice_button)
        
        # Add widgets to layout
        layout.addWidget(self.sequence_generator)
        layout.addWidget(self.practice_widget)
        layout.addWidget(self.favorites_widget)
        layout.addWidget(self.poses_widget)

        # Create container widget and set layout
        container = QWidget()
        container.setLayout(layout)

        # Set as central widget
        self.setCentralWidget(container)

    def hide_all_widgets(self):
        """Hide main buttons and all page widgets."""
        for button in self.main_buttons:
            button.setVisible(False)
        for widget in self.all_widgets:
            widget.setVisible(False)

    def show_main_buttons(self):
        """Show main navigation buttons."""
        for button in self.main_buttons:
            button.setVisible(True) 

    def back_to_main(self):
        """Return to main page."""
        self.show_main_page()
    
    def show_main_page(self):
        """Display the main page with navigation buttons."""
        self.hide_all_widgets()
        self.show_main_buttons()
        self.setWindowTitle(self.main_title)
        logger.info("Returned to main page")

    def generate_button_was_clicked(self):
        """Handle generate sequence button click."""
        print("Generate a sequence was clicked.")
        self.setWindowTitle(self.main_title + " - Generate a Sequence")
        self.hide_all_widgets()
        
        # Refresh data if needed
        if hasattr(self.sequence_generator, 'refresh_data'):
            self.sequence_generator.refresh_data()
        
        self.sequence_generator.setVisible(True)

    def sequences_button_was_clicked(self):
        """Handle sequences button click (updated from favorites)."""
        print("View sequences was clicked.")
        self.setWindowTitle(self.main_title + " - My Sequences")
        self.hide_all_widgets()
        
        # Refresh sequences data
        if hasattr(self.favorites_widget, 'refresh_favorites'):
            self.favorites_widget.refresh_favorites()
        
        self.favorites_widget.setVisible(True)

    def favorites_button_was_clicked(self):
        """Backward compatibility - redirect to sequences."""
        self.sequences_button_was_clicked()

    def poses_button_was_clicked(self):
        """Handle poses button click."""
        print("View all poses was clicked.")
        self.setWindowTitle(self.main_title + " - All Poses")
        self.hide_all_widgets()
        
        # Refresh pose data and load images
        if hasattr(self.poses_widget, 'refresh_data'):
            self.poses_widget.refresh_data()
        
        if hasattr(self.poses_widget, 'load_pose_images'):
            self.poses_widget.load_pose_images()
        
        self.poses_widget.setVisible(True)

    def practice_button_was_clicked(self):
        """Handle practice mode button click."""
        print("Practice mode was clicked.")
        self.setWindowTitle(self.main_title + " - Practice Mode")
        self.hide_all_widgets()
        
        # Refresh practice widget data
        if hasattr(self.practice_widget, 'refresh_sequences'):
            self.practice_widget.refresh_sequences()
        
        self.practice_widget.setVisible(True)

    def clear_all_caches(self):
        """Clear all application caches."""
        try:
            clear_image_cache()
            from utils import cleanup_all_caches
            cleanup_all_caches()
            
            show_success_message(
                self, 
                "Cache Cleared", 
                "All caches have been cleared successfully. Memory usage should be reduced."
            )
            logger.info("All caches cleared")
            
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")
            show_error_message(self, "Cache Error", f"Error clearing caches: {str(e)}")

    def show_cache_stats(self):
        """Display cache statistics."""
        try:
            from utils import get_system_stats
            stats = get_system_stats()
            
            image_stats = stats.get("image_cache", {})
            display_stats = stats.get("display_cache", {})
            
            stats_text = f"""
Image Cache:
• Entries: {image_stats.get('entries', 0)}
• Memory: {image_stats.get('memory_mb', 0):.1f} MB
• Hit Rate: {image_stats.get('hit_rate_percent', 0):.1f}%

Display Cache:
• Format Cache: {display_stats.get('format_cache_size', 0)} entries

Database: {'Connected' if stats.get('database_connected', False) else 'Disconnected'}
            """
            
            show_success_message(self, "Cache Statistics", stats_text.strip())
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            show_error_message(self, "Stats Error", f"Error getting statistics: {str(e)}")

    def closeEvent(self, event):
        """Handle application close event."""
        try:
            # Clean up caches before closing
            clear_image_cache()
            logger.info("Application closing - caches cleared")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        event.accept()

    def refresh_all_data(self):
        """Refresh data in all widgets."""
        try:
            # Refresh sequence generator
            if hasattr(self.sequence_generator, 'refresh_data'):
                self.sequence_generator.refresh_data()
            
            # Refresh favorites/sequences widget
            if hasattr(self.favorites_widget, 'refresh_favorites'):
                self.favorites_widget.refresh_favorites()
            
            # Refresh poses widget
            if hasattr(self.poses_widget, 'refresh_data'):
                self.poses_widget.refresh_data()
            
            # Refresh practice widget
            if hasattr(self.practice_widget, 'refresh_sequences'):
                self.practice_widget.refresh_sequences()
            
            logger.info("All widget data refreshed")
            
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")

    # Legacy method for backward compatibility
    def build_image_cache(self):
        """Legacy method - now handled by initialize_image_cache."""
        self.initialize_image_cache()