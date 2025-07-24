from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QHBoxLayout
import json
import os
from config import FAVORITES_FILE

class FavoritesWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        if os.path.exists(FAVORITES_FILE):
            print(f"Loading favorites from {FAVORITES_FILE}")
            with open(FAVORITES_FILE, 'r') as f:
                favorites_data = json.load(f)
        else:
            favorites_data = {"favorites": []}
        
        if len(favorites_data["favorites"]) == 0:
            empty_message = QLabel("No favorites saved yet. Generate a sequence and favorite it!")
            layout.addWidget(empty_message)
            print(f"There are no favorites yet. Generate a sequence so you can save one!")
        else:#Generate Favorites
            # Create scrollable area for favorites
            scroll_area = QScrollArea()
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout()
            for favorite in favorites_data["favorites"]:
                # Create card container
                card_widget = QWidget()
                card_layout = QVBoxLayout()
                
                # Big sequence name
                name_label = QLabel(favorite["name"])
                
                
                # Metadata (date, duration)
                meta_info = QLabel(f"Created: {favorite['created_date']} | Duration: {favorite['duration']}")
                meta_info.setStyleSheet("color: #666; font-size: 12px;")
                
                 # Hidden sequences section (initially hidden)
                sequences_widget = QWidget()
                sequences_layout = QVBoxLayout()

                # Expand/collapse button for sequences
                expand_btn = QPushButton("▶ Show Sequences")
                expand_btn.clicked.connect(lambda checked, widget=sequences_widget, btn=expand_btn: self.toggle_sequences(widget, btn))
                
                # Add sequence content here
                section_map = {
                    "warm_up":"WARM UP",
                    "main_flow":"MAIN FLOW",
                    "cool_down":"COOL DOWN"
                }
                favorite_sequence = ""
                counter = 1
                for section_key, sequence_list in favorite['sequences'].items():
                    favorite_sequence += f'=== {section_map[section_key]} ===\n'
                    for sequence in sequence_list:
                        favorite_sequence+= str(counter) + '. ' + sequence['name'] + '\n'
                        counter += 1
                    
                sequences_label = QLabel(favorite_sequence)
                sequences_layout.addWidget(sequences_label)
                sequences_label.setStyleSheet("font-family: monospace; padding: 10px; background-color: #f8f8f8; border-radius: 4px; line-height: 1.4;")
                sequences_label.setStyleSheet("font-size: 18px; font-weight: bold;")

                sequences_widget.setLayout(sequences_layout)
                sequences_widget.setVisible(False)  # Start collapsed
                
                # Action buttons
                button_layout = QHBoxLayout()
                details_btn = QPushButton("Details")
                delete_btn = QPushButton("Delete") 
                practice_btn = QPushButton("Practice")

                button_layout.addWidget(details_btn)
                button_layout.addWidget(practice_btn)
                button_layout.addWidget(delete_btn)
                                
                # Add everything to card
                card_layout.addWidget(name_label)
                card_layout.addWidget(meta_info)
                card_layout.addWidget(expand_btn)
                card_layout.addWidget(sequences_widget)
                card_layout.addLayout(button_layout)
                
                card_widget.setLayout(card_layout)
                scroll_layout.addWidget(card_widget)
    
            scroll_content.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_content)
            scroll_area.setWidgetResizable(True)  # Important for proper scrolling
            layout.addWidget(scroll_area)
            

        self.setLayout(layout)

    def toggle_sequences(self,sequences_widget,button):
        if sequences_widget.isVisible():
            sequences_widget.setVisible(False)
            button.setText("▶ Show Sequence")
        else:
            sequences_widget.setVisible(True)
            button.setText("▼ Hide Sequence")