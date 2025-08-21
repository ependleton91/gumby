from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QHBoxLayout, QMessageBox
from gui.dialogs.details_dialog import details_dialog_box
from utils.file_utils import load_favorites_data,save_favorites_data
from utils.ui_utils import show_error_message,show_success_message,confirm_sequence_delete

class FavoritesWidget(QWidget):
    def create_favorites_display(self):
        # Create scrollable area for favorites
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        # Load favorites data
        favorites_data = load_favorites_data()


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

    def refresh_favorites(self):
        # Same refresh logic as in delete_favorite
        self.layout().removeWidget(self.scroll_area)
        self.scroll_area.deleteLater()
        new_scroll_area = self.create_favorites_display()
        self.layout().addWidget(new_scroll_area)
        self.scroll_area = new_scroll_area
        print("refresh requested!")

    def toggle_sequences(self,sequences_widget,button):
        #On click, make opposite of current status 
        if sequences_widget.isVisible():
            sequences_widget.setVisible(False)
            button.setText("▶ Show Sequence")
        else:
            sequences_widget.setVisible(True)
            button.setText("▼ Hide Sequence")

    def delete_favorite(self, favorite):
        # Confirm Deletion
        print(f"Attempting to delete favorite: {favorite['name']}")
        
        if confirm_sequence_delete(self, favorite['name']):
            print(f"User selected 'YES'")
            # Remove from json
            favorites_data = load_favorites_data()

            # Find and remove the favorite
            for item in favorites_data["favorites"]:
                if item['name'] == favorite['name']:
                    favorites_data["favorites"].remove(item)
                    break
                    
            # Save updated favorites    
            favorites_saved = save_favorites_data(favorites_data)
            print(f"Deleted favorite: {favorite['name']}")
            
            # Show success message
            if favorites_saved:
                show_success_message(self, "Favorite Deleted", f"Successfully deleted {favorite['name']} from favorites.")
            else:
                show_error_message(self, "Deletion Failed", f"Failed to delete {favorite['name']} from favorites. File not saved.")

            # Refresh page
            self.layout().removeWidget(self.scroll_area)
            self.scroll_area.deleteLater()
            new_scroll_area = self.create_favorites_display()
            self.layout().addWidget(new_scroll_area)
            self.scroll_area = new_scroll_area
        else:
            print(f"User selected 'NO'")
    
    def show_details(self,favorite):
        dialog = details_dialog_box(favorite)
        dialog.exec()
        self.refresh_favorites()

  