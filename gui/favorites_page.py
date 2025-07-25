from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QHBoxLayout, QMessageBox
import json
import os
from config import FAVORITES_FILE
from gui.dialogs.details_dialogue import details_dialogue_box

class FavoritesWidget(QWidget):
    def create_favorites_display(self):
        # Create scrollable area for favorites
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        if os.path.exists(FAVORITES_FILE):
            print(f"Loading favorites from {FAVORITES_FILE}")
            with open(FAVORITES_FILE, 'r') as f:
                favorites_data = json.load(f)
        else:
            favorites_data = {"favorites": []}
        
        if len(favorites_data["favorites"]) == 0:
            empty_message = QLabel("No favorites saved yet. Generate a sequence and favorite it!")
            scroll_layout.addWidget(empty_message)
            print(f"There are no favorites yet. Generate a sequence so you can save one!")
        else:#Generate Favorites
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
                    
                # map ui title to results title
                section_map = {
                    "warm_up":"WARM UP",
                    "main_flow":"MAIN FLOW",
                    "cool_down":"COOL DOWN"
                    }

                #initialize sequence string
                favorite_sequence = ""
                counter = 1
                for section_key, sequence_list in favorite['sequences'].items():
                    favorite_sequence += f'=== {section_map[section_key]} ===\n'
                    for sequence in sequence_list:
                        favorite_sequence+= str(counter) + '. ' + sequence['name'] + '\n'
                        counter += 1

                #Add populated sequence to layout  
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

                delete_btn.clicked.connect(lambda checked, fav = favorite: self.delete_favorite(fav))
                details_btn.clicked.connect(lambda checked, fav=favorite: self.show_details(fav))

                #Add buttons to button layout
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
              #create a card for each favorite in json
                scroll_layout.addWidget(card_widget)
    
        #Set scroll deetz
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True) 
           
        return scroll_area
             
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.scroll_area = self.create_favorites_display()
        layout.addWidget(self.scroll_area)    
        self.setLayout(layout)

    def toggle_sequences(self,sequences_widget,button):
        #On click, make opposite of current status 
        if sequences_widget.isVisible():
            sequences_widget.setVisible(False)
            button.setText("▶ Show Sequence")
        else:
            sequences_widget.setVisible(True)
            button.setText("▼ Hide Sequence")

    def delete_favorite(self,favorite):
        #Confirm Deletion
        selection = QMessageBox.question(
            self, 
            "Delete Favorite", 
            f"Are you sure you want to delete {favorite['name']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
            )

        if selection == QMessageBox.StandardButton.Yes:
            print(f"User selected 'YES'")
            # Remove from json
            with open(FAVORITES_FILE, 'r') as f:
                favorites_data = json.load(f)

            for item in favorites_data["favorites"]:
                if item['name'] == favorite['name']:
                    favorites_data["favorites"].remove(item)
                    break

            with open(FAVORITES_FILE, 'w') as f:
                json.dump(favorites_data, f, indent=2)
            # Refresh page
            self.layout().removeWidget(self.scroll_area)
            self.scroll_area.deleteLater()
            new_scroll_area = self.create_favorites_display()
            self.layout().addWidget(new_scroll_area)
            self.scroll_area = new_scroll_area
            
        else:
            print(f"User selected 'NO'")
        # User clicked No, so return early
        return
    
    def show_details(self,favorite):
        dialog = details_dialogue_box(favorite)
        dialog.exec()

  