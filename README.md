# Yoga Sequence Builder

A visual application for creating, customizing, and managing yoga sequences. Generate classes based on duration, style, and target muscle groups.

## Features

- Smart Sequence Generation: Create sequences based on class duration, style (Yin, Vinyasa, Hatha), and target muscle groups
- Visual Pose Library: Browse poses with images and detailed instructions
- Sequence Management: Save, edit, and organize your favorite sequences
- Class Builder: Combine sequences into complete yoga classes
- Export Options: Share sequences with students or other instructors

## Quick Start (For Everyone)

### Option 1: Simple Installation (Recommended)
```bash
# Download and setup (paste this in Terminal)
git clone https://github.com/yourusername/yoga-sequence-app.git
cd yoga-sequence-app
bash setup.sh
Option 2: Manual Installation

Install Python (if you don't have it):

Visit python.org and download Python 3.11+
Or use Homebrew: brew install python


Get the app:
bashgit clone https://github.com/yourusername/yoga-sequence-app.git
cd yoga-sequence-app

Set up environment:
bashpython3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Run the app:
bashpython main.py


System Requirements

Operating System: macOS 10.14+, Windows 10+, or Linux
Python: 3.11 or higher
Memory: 2GB RAM minimum, 4GB recommended
Storage: 500MB free space

How to Use
Creating Your First Sequence

Launch the app: python main.py
Click "Generate New Sequence"
Set your preferences:

Class duration (15-90 minutes)
Style (Yin, Vinyasa, Hatha)
Target areas (abs, arms, back, etc.)


Click "Generate" and review your sequence
Save sequences you like for future use

Managing Sequences

View All: Browse your saved sequences in the library
Edit: Modify existing sequences by adding/removing poses
Favorite: Star sequences for quick access
Export: Share sequences as PDF or text

Building Full Classes

Combine multiple sequences into complete classes
Add warm-up, main flow, and cool-down sections
Preview total class duration and flow

For Developers
Project Structure
yoga_sequence_app/
├── main.py                     # Application entry point
├── config.py                   # App configuration and constants
├── requirements.txt            # Python dependencies
├── data/                       # Data models and file operations
│   ├── models.py              # Pydantic data models
│   ├── sequence_manager.py    # JSON file operations
│   └── pose_library.py        # Pose data handling
├── core/                      # Business logic
│   ├── sequence_generator.py  # Sequence creation algorithms
│   ├── class_builder.py       # Full class assembly
│   └── filters.py             # Search and filter logic
├── ui/                        # GUI components (PyQt6)
│   ├── main_window.py         # Primary interface
│   ├── sequence_editor.py     # Sequence editing interface
│   ├── preview_panel.py       # Sequence preview and display
│   └── dialogs.py             # Modal dialogs and popups
├── assets/                    # Static resources
│   ├── images/poses/          # Pose images
│   └── styles/                # UI styling files
├── app_data/                  # User data (created at runtime)
│   ├── sequences.json         # Sequence database
│   ├── user_favorites.json    # User's favorite sequences
│   └── user_settings.json     # Application preferences
└── tests/                     # Test suite
    ├── test_data.py           # Data layer tests
    ├── test_core.py           # Business logic tests
    └── test_ui.py             # UI component tests
Development Setup
bash# Clone and setup
git clone https://github.com/yourusername/yoga-sequence-app.git
cd yoga-sequence-app

# Create development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8

# Run tests
pytest

# Format code
black .
Key Technologies

GUI Framework: PyQt6 (cross-platform native UI)
Data Validation: Pydantic (type-safe data models)
Image Processing: Pillow (pose image handling)
Data Storage: JSON files (human-readable, version-controllable)

Contributing

Fork the repository
Create a feature branch: git checkout -b feature-name
Make your changes and add tests
Ensure code passes: pytest && black . && flake8
Submit a pull request

Adding New Poses

Add pose image to assets/images/poses/
Update pose data in app_data/sequences.json
Follow the existing data structure:
json{
  "name": "Pose Name",
  "duration": 30,
  "difficulty": 2,
  "body_parts": ["target_areas"],
  "class_types": ["applicable_styles"]
}


Troubleshooting
Common Issues
"Command not found: python"

Try python3 instead of python
Install Python from python.org

"No module named PyQt6"

Activate your virtual environment: source venv/bin/activate
Install dependencies: pip install -r requirements.txt

App won't start on macOS

You may need to allow the app in Security & Privacy settings
Or run: xattr -cr yoga-sequence-app

Missing pose images

Ensure you have the complete repository
Check that assets/images/poses/ contains image files

Getting Help

Issues: Report bugs on GitHub Issues
Discussions: Ask questions in GitHub Discussions
Email: Contact developer at your-email@example.com

Data Format
Sequences are stored in JSON format for easy editing and version control:
json{
  "sequences": {
    "sun_salutation_a": {
      "name": "Sun Salutation A",
      "category": "flow_warmup",
      "poses": [
        {"name": "Mountain Pose", "duration": 15},
        {"name": "Upward Salute", "duration": 15}
      ],
      "total_duration": 225,
      "difficulty": 2,
      "body_parts": ["full_body", "shoulders"],
      "class_types": ["vinyasa", "hatha"]
    }
  }
}
Building Standalone App
For macOS Users
bash# Install packaging tool
pip install py2app

# Create standalone app
python setup.py py2app

# App will be in dist/YogaSequenceBuilder.app
For All Platforms
bash# Install PyInstaller
pip install pyinstaller

# Create single executable
pyinstaller --onefile --windowed main.py

Pose database inspired by traditional yoga teachings
UI design principles from modern macOS applications
Built with love for the yoga community


Version: 1.0.0
Last Updated: July 2025
Compatibility: Python 3.11+, macOS 10.14+, Windows 10+, Linux
For the latest updates and releases, visit: 