GUMBY - Yoga Sequence Generator

A desktop application for generating, practicing, and managing yoga sequences built with Python and PyQt6.

   What This Application Does

GUMBY is a comprehensive yoga practice companion that helps you create personalized yoga sequences based on your preferences and practice them with guided timing. The app provides four main features through an intuitive desktop interface:

  1.  Generate Sequences 
- Create custom yoga classes by selecting:
  - Duration (15-90 minutes via slider)
  - Style (Yin, Hatha, or Vinyasa)
  - Target muscle groups (Abs, Arms, Back, Pelvic Floor, or All)
- Intelligent sequence building that:
  - Follows proper class structure (warm-up → main flow → cool-down)
  - Respects style-specific timing ratios
  - Ensures muscle group coverage meets your targets
  - Uses scoring algorithm to optimize sequence selection

  2.  Favorites Management 
- Save generated sequences you love
- Add custom names and descriptions
- View detailed breakdowns of each sequence
- Edit favorite details (name, description)
- Delete sequences you no longer need
- Expandable/collapsible sequence views for easy browsing

  3.  All Poses Library 
- Browse comprehensive pose database with images
- View detailed pose information including:
  - Instructions and modifications
  - Target muscle groups and difficulty levels
  - Default durations and pose types
-  Edit and create poses  through intuitive forms
- Upload custom pose images for new or existing poses
- Organized in clean card-based grid layout

  4.  Practice Mode 
- Select any favorited sequence for guided practice
- Interactive timer system with:
  - Visual countdown for each pose
  - Play/pause controls
  - Skip forward/backward between poses
  - Progress tracking (pose X of Y)
- Real-time pose images during practice
- Session completion tracking with:
  - Practice duration recording
  - Personal rating system (1-5 stars)
  - Custom notes for reflection
- Practice history saved to each favorite sequence

  Technical Implementation

  Architecture
-  Frontend : PyQt6 for cross-platform desktop GUI
-  Data Storage : JSON files for sequences, poses, favorites, and practice history
-  Structure : Organized MVC-style with separate modules for:
  - GUI components (`gui/`)
  - Business logic (`services/`)
  - Data models and storage (`data/`, `models/`)
  - Configuration (`config.py`)

  Key Features
-  Image Caching : Efficient pose image loading and management
-  Responsive UI : Adapts to screen size with proper scaling
-  Navigation : Menu bar + button-based navigation between sections
-  Dialog System : Modal dialogs for editing, details, and confirmations
-  Smart Sequence Building : Algorithm considers duration, style, muscle targets, and energy flow

  Data Management
-  Sequences : Pre-built flow sequences with categorization and metadata
-  Poses : Individual pose database with instructions and images
-  Favorites : User-saved sequences with practice history
-  Settings : Centralized configuration management

  File Structure

```
gumby/
├── main.py                            Application entry point
├── config.py                          Settings and file paths
├── requirements.txt                   Python dependencies
├── gui/
│   ├── main_window.py                Main application window
│   ├── sequence_generator.py         Sequence creation interface
│   ├── favorites_page.py             Favorites management
│   ├── all_poses.py                 Pose library browser
│   ├── practice_mode.py             Guided practice interface
│   └── dialogs/                     Modal dialog components
├── services/
│   └── build_sequence.py            Sequence generation logic
├── app_data/
│   └── sequences.json               Pre-built sequence database
├── assets/
│   └── styles/style.qss            Application styling
└── models/ & data/                  Data structures (planned)
```

  Installation & Setup

1.  Requirements : Python 3.8+ with PyQt6
   ```bash
   pip install -r requirements.txt
   ```

2.  Run Application :
   ```bash
   python main.py
   ```

3.  First Use : The app will create necessary data files automatically

  Future Development Plans

  Immediate Enhancements
- [ ]  Sequence Templates : Add more pre-built sequences for different skill levels and focuses
- [ ]  Pose Image Library : Expand pose database with high-quality demonstration images
- [ ]  Export Features : Save sequences as PDF guides or export practice schedules
- [ ]  Music Integration : Add background music options during practice sessions

  Advanced Features
- [ ]  Voice Guidance : Text-to-speech for pose instructions and transitions
- [ ]  Progress Analytics : Track practice frequency, favorite styles, and improvement metrics
- [ ]  Sequence Sharing : Import/export sequences to share with friends or teachers
- [ ]  Advanced Filtering : Search poses by difficulty, duration, or specific benefits

  User Experience
- [ ]  Keyboard Shortcuts : Add hotkeys for common actions during practice
- [ ]  Customizable Themes : Dark mode and color scheme options
- [ ]  Accessibility : Screen reader support and high contrast modes
- [ ]  Multi-language : Internationalization for global yoga community

  Integration Possibilities
- [ ]  Wearable Devices : Heart rate monitoring during practice
- [ ]  Calendar Integration : Schedule practice sessions
- [ ]  Health Apps : Sync with fitness trackers and wellness platforms
- [ ]  Social Features : Connect with yoga communities and teachers

  Contributing

This is a personal project built for learning and practice management. The codebase is organized with clean separation of concerns and modular components to facilitate future enhancements and maintenance.