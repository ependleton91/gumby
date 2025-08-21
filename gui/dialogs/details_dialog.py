from PyQt6.QtWidgets import QDialog, QMessageBox,QPushButton,QLineEdit,QTabWidget,QLabel,QVBoxLayout,QHBoxLayout,QTextEdit, QDialogButtonBox,QWidget,QListWidget,QGroupBox, QInputDialog,QLabel,QTreeWidget, QTreeWidgetItem, QSplitter,QScrollArea
from PyQt6.QtCore import Qt
from utils.file_utils import load_favorites_data, save_favorites_data, load_flows_data
from utils.ui_utils import show_error_message, show_success_message
from utils.validation_utils import validate_sequence_name, validate_yoga_style
from utils.datetime_utils import format_duration_minutes


class details_dialog_box(QDialog):
        def __init__(self,favorite):
            super().__init__()
            self.favorite = favorite
            tab_widget = QTabWidget()
            tab_widget.addTab(General_Tab(self.favorite),"GENERAL")
            tab_widget.addTab(Sequence_Tab(self.favorite),"SEQUENCE")
            tab_widget.addTab(History_Tab(self.favorite),"HISTORY")


            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)

            button_box.clicked.connect(self.accept)

            main_layout = QVBoxLayout()
            main_layout.addWidget(tab_widget)
            main_layout.addWidget(button_box)
            self.setLayout(main_layout)
            self.setWindowTitle(f"Favorite Details: {self.favorite['name']}")

class General_Tab(QWidget):
    def __init__(self, favorite):
        super().__init__()
        self.favorite = favorite
        self.main_layout = QVBoxLayout()

        # NAME
        self.name_layout = QHBoxLayout()
        name_label = QLabel("NAME:")
        self.name_content = QLabel(self.favorite['name'])
        self.name_layout.addWidget(name_label)
        self.name_layout.addWidget(self.name_content)
        self.main_layout.addLayout(self.name_layout) 

        #STYLE
        style_layout = QHBoxLayout()
        style_label = QLabel("STYLE:")
        style_content = QLabel(self.favorite['style'])
        style_layout.addWidget(style_label)
        style_layout.addWidget(style_content)
        self.main_layout.addLayout(style_layout) 

        #CREATED DATE
        created_layout = QHBoxLayout()
        created_label = QLabel("CREATED DATE:")
        created_content = QLabel(self.favorite['created_date'])
        created_layout.addWidget(created_label)
        created_layout.addWidget(created_content)
        self.main_layout.addLayout(created_layout) 

        # DURATION
        duration_layout = QHBoxLayout()
        duration_label = QLabel("DURATION:")
        self.duration_content = QLabel(self.favorite['duration'])
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_content)
        self.main_layout.addLayout(duration_layout) 

        #MUSCLES
        muscles_layout = QHBoxLayout()
        muscles_label = QLabel("MUSCLES TARGETED:")
        muscles_content = QLabel(", ".join(self.favorite['muscles']))
        muscles_layout.addWidget(muscles_label)
        muscles_layout.addWidget(muscles_content)
        self.main_layout.addLayout(muscles_layout) 

        #DESCRIPTION
        description_layout = QHBoxLayout()
        description_label = QLabel("DESCRIPTION:")
        self.description_content = QTextEdit(self.favorite['description'])
        self.description_content.setReadOnly(True)
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_content)
        self.main_layout.addLayout(description_layout) 

        
        bottom_content = QWidget()
        bottom_buttons = QHBoxLayout()


        self.edit_mode = False
        self.edit_button = QPushButton("EDIT")
        self.edit_button.setVisible(True)
        self.edit_button.clicked.connect(self.enter_edit_mode)
        bottom_buttons.addWidget(self.edit_button)

        self.save_button = QPushButton("SAVE")
        self.save_button.setVisible(False)
        self.save_button.clicked.connect(self.save_changes)
        bottom_buttons.addWidget(self.save_button)

        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self.cancel_edit)
        bottom_buttons.addWidget(self.cancel_button)

        bottom_content.setLayout(bottom_buttons)

        
        self.main_layout.addWidget(bottom_content)
        self.setLayout(self.main_layout)

    def enter_edit_mode(self):

        self.edit_button.setVisible(False)
        self.save_button.setVisible(True)
        self.cancel_button.setVisible(True)
        self.edit_mode = True
        self.description_content.setReadOnly(False)

        self.original_name = self.favorite['name']
        self.original_description = self.favorite['description']

        self.name_content.setVisible(False)
        self.name_edit=QLineEdit(self.favorite["name"])
        self.name_edit.setReadOnly(False)
        self.name_layout.addWidget(self.name_edit)

    def refresh_duration(self):
        """Update the displayed duration when sequence changes."""
        if hasattr(self, 'duration_content'):
            self.duration_content.setText(self.favorite['duration'])
    
    def save_changes(self):
        try:
            favorites_data = load_favorites_data()

            new_name = self.name_edit.text().strip()
            new_description = self.description_content.toPlainText().strip()

            is_valid_name, name_error = validate_sequence_name(new_name)
            if not is_valid_name:
                show_error_message("Invalid Name", name_error)
                return  

            for favorite in favorites_data["favorites"]:
                    if favorite["created_date"] == self.favorite["created_date"]:
                        favorite["name"] = new_name
                        favorite["description"] = new_description
                        break
            
            self.favorite["name"] = new_name
            self.favorite["description"] = new_description
            self.parent().setWindowTitle(f"Favorite Details: {self.favorite['name']}")

            favorite_saved = save_favorites_data(favorites_data)
            if favorite_saved:
                show_success_message(self,"Favorite Saved", f"Successfully saved '{new_name}' to favorites.")
            else:
                show_error_message(self,"Save Failed", "Failed to save favorite."," please try again.")

            self.exit_edit_mode()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save changes: {str(e)}")
            return

    def cancel_edit(self):
        self.favorite["name"] = self.original_name
        self.favorite["description"] = self.original_description
        
        # Reset edit widgets to original values
        self.name_edit.setText(self.original_name)
        self.description_content.setText(self.original_description)
        self.exit_edit_mode()
        
    def exit_edit_mode(self):

        self.edit_button.setVisible(True)
        self.save_button.setVisible(False)
        self.cancel_button.setVisible(False)
        self.edit_mode = False
        self.description_content.setReadOnly(True)
        self.name_content.setVisible(True)
        self.name_edit.setVisible(False)
        self.name_content.setText(self.favorite["name"]) 

class Sequence_Tab(QWidget):
    def __init__(self, favorite):
        super().__init__()
        self.favorite = favorite
        self.edit_mode = False
        
        main_layout = QVBoxLayout()
        
        # Header with edit button
        header_layout = QHBoxLayout()
        header_label = QLabel("SEQUENCE DETAILS")
        header_layout.addWidget(header_label)
        
        self.edit_button = QPushButton("Edit Sequence")
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        header_layout.addWidget(self.edit_button)
        
        main_layout.addLayout(header_layout)
        
        # Create the enhanced sequence view
        self.create_enhanced_sequence_view(main_layout)
        
        self.setLayout(main_layout)
    
    def create_enhanced_sequence_view(self, main_layout):
        # Create splitter for side-by-side layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Sequence tree view
        sequence_widget = self.create_sequence_tree()
        splitter.addWidget(sequence_widget)
        
        # Right side: Flow details
        details_widget = self.create_flow_details_panel()
        splitter.addWidget(details_widget)
        
        splitter.setSizes([400, 300])
        main_layout.addWidget(splitter)
        
        # Edit buttons (initially hidden)
        self.create_edit_buttons(main_layout)
    
    def create_sequence_tree(self):
        widget = QGroupBox("Flows in Sequence")
        layout = QVBoxLayout()
        
        self.sequence_tree = QTreeWidget()
        self.sequence_tree.setHeaderLabels(["Flow Name", "Duration", "Difficulty"])
        self.sequence_tree.itemClicked.connect(self.on_flow_selected)
        
        layout.addWidget(self.sequence_tree)
        widget.setLayout(layout)
        
        self.populate_sequence_tree()
        return widget
    
    def create_flow_details_panel(self):
        widget = QGroupBox("Flow Details")
        layout = QVBoxLayout()
        
        self.flow_name_label = QLabel("Click a flow to see details")
        self.flow_info_label = QLabel("")
        
        layout.addWidget(self.flow_name_label)
        layout.addWidget(self.flow_info_label)
        
        poses_label = QLabel("Poses in this flow:")
        poses_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(poses_label)
        
        self.poses_list = QListWidget()
        self.poses_list.setMaximumHeight(150)
        layout.addWidget(self.poses_list)
        
        widget.setLayout(layout)
        return widget
    
    def create_edit_buttons(self, main_layout):
        self.edit_buttons_widget = QWidget()
        button_layout = QHBoxLayout()
        
        self.add_flow_btn = QPushButton("Add Flow")
        self.remove_flow_btn = QPushButton("Remove Flow")
        self.move_up_btn = QPushButton("Move Up")
        self.move_down_btn = QPushButton("Move Down")
        self.save_btn = QPushButton("Save Changes")
        self.cancel_btn = QPushButton("Cancel")
        
        button_layout.addWidget(self.add_flow_btn)
        button_layout.addWidget(self.remove_flow_btn)
        button_layout.addWidget(self.move_up_btn)
        button_layout.addWidget(self.move_down_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        self.edit_buttons_widget.setLayout(button_layout)
        self.edit_buttons_widget.setVisible(False)  # Start hidden
        
        main_layout.addWidget(self.edit_buttons_widget)
        
        # Connect button actions
        self.add_flow_btn.clicked.connect(self.add_flow)
        self.remove_flow_btn.clicked.connect(self.remove_flow)
        self.move_up_btn.clicked.connect(self.move_flow_up)
        self.move_down_btn.clicked.connect(self.move_flow_down)
        self.save_btn.clicked.connect(self.save_changes)
        self.cancel_btn.clicked.connect(self.cancel_edit)
    
    def populate_sequence_tree(self):
        self.sequence_tree.clear()
        
        section_names = {
            "warm_up": "🔥 Warm Up",
            "main_flow": "💪 Main Flow",
            "cool_down": "🧘 Cool Down"
        }
        
        for section_key, flows in self.favorite["sequences"].items():
            section_item = QTreeWidgetItem([section_names.get(section_key, section_key.title()), "", ""])
            section_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "section", "key": section_key})
            
            for flow in flows:
                flow_item = QTreeWidgetItem([
                    flow["name"],
                    f"{flow['duration']} min", 
                    f"{flow['difficulty']}/5"
                ])
                flow_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "flow", "data": flow})
                section_item.addChild(flow_item)
            
            self.sequence_tree.addTopLevelItem(section_item)
            section_item.setExpanded(True)
    
    def on_flow_selected(self, item, column):
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_data and item_data["type"] == "flow":
            self.display_flow_details(item_data["data"])
    
    def display_flow_details(self, flow_data):
        self.flow_name_label.setText(f"Flow: {flow_data['name']}")
        
        info_text = (f"Duration: {flow_data['duration']} minutes\n"
                    f"Category: {flow_data['category']}\n"
                    f"Style: {', '.join(flow_data['style'])}\n"
                    f"Difficulty: {flow_data['difficulty']}/5\n"
                    f"Energy: {flow_data['energy_level']}")
        
        self.flow_info_label.setText(info_text)
        
        self.poses_list.clear()
        for pose in flow_data.get("flow", []):
            duration_text = format_duration_minutes(pose.get("duration", 0.5))
            self.poses_list.addItem(f"{pose['name']} ({duration_text})")
    
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        
        if self.edit_mode:
            self.edit_button.setText("Cancel Edit")
            self.edit_buttons_widget.setVisible(True)
        else:
            self.edit_button.setText("Edit Sequence")
            self.edit_buttons_widget.setVisible(False)
    
    def add_flow(self):
        current_item = self.sequence_tree.currentItem()
        if not current_item:
            return
        
        # Find section
        section_item = current_item
        if current_item.data(0, Qt.ItemDataRole.UserRole)["type"] == "flow":
            section_item = current_item.parent()
        
        section_key = section_item.data(0, Qt.ItemDataRole.UserRole)["key"]
        
        # Get available flows
        flows_data = load_flows_data()
        available_flows = list(flows_data.get("flowing_sequences", {}).values())
        flow_names = [flow["name"] for flow in available_flows]
        
        if not flow_names:
            return
        
        flow_name, ok = QInputDialog.getItem(
            self, "Add Flow", f"Select a flow for {section_key}:", 
            flow_names, 0, False
        )
        
        if ok and flow_name:
            selected_flow = next((f for f in available_flows if f["name"] == flow_name), None)
            if selected_flow:
                self.favorite["sequences"][section_key].append(selected_flow.copy())
                self.recalculate_total_duration()  
                self.populate_sequence_tree()

    def remove_flow(self):
        current_item = self.sequence_tree.currentItem()
        if not current_item:
            return
        
        item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if item_data["type"] != "flow":
            return
        
        section_item = current_item.parent()
        section_key = section_item.data(0, Qt.ItemDataRole.UserRole)["key"]
        flow_index = section_item.indexOfChild(current_item)
        
        del self.favorite["sequences"][section_key][flow_index]
        self.recalculate_total_duration()  # ← ADD THIS LINE
        self.populate_sequence_tree()
    
    def move_flow_up(self):
        current_item = self.sequence_tree.currentItem()
        if not current_item:
            return
        
        item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if item_data["type"] != "flow":
            return
        
        section_item = current_item.parent()
        section_key = section_item.data(0, Qt.ItemDataRole.UserRole)["key"]
        flow_index = section_item.indexOfChild(current_item)
        
        if flow_index > 0:
            flows = self.favorite["sequences"][section_key]
            flows[flow_index], flows[flow_index - 1] = flows[flow_index - 1], flows[flow_index]
            self.populate_sequence_tree()
    
    def move_flow_down(self):
        current_item = self.sequence_tree.currentItem()
        if not current_item:
            return
        
        item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if item_data["type"] != "flow":
            return
        
        section_item = current_item.parent()
        section_key = section_item.data(0, Qt.ItemDataRole.UserRole)["key"]
        flow_index = section_item.indexOfChild(current_item)
        flows = self.favorite["sequences"][section_key]
        
        if flow_index < len(flows) - 1:
            flows[flow_index], flows[flow_index + 1] = flows[flow_index + 1], flows[flow_index]
            self.populate_sequence_tree()
    
    def save_changes(self):
        favorites_data = load_favorites_data()
        for fav in favorites_data["favorites"]:
            if fav["created_date"] == self.favorite["created_date"]:
                fav["sequences"] = self.favorite["sequences"]
                fav["duration"] = self.favorite["duration"] 

                break
        
        save_favorites_data(favorites_data)
        self.toggle_edit_mode()  # Exit edit mode
        
        from utils.ui_utils import show_success_message
        show_success_message(self, "Sequence Updated", "Your sequence changes have been saved!")
    
    def cancel_edit(self):
        # Could reload original data here if you want to discard changes
        self.toggle_edit_mode()

    def recalculate_total_duration(self):
        """Recalculate and update the total sequence duration when flows change."""
        total_duration = 0
        
        print("=== DURATION CALCULATION DEBUG ===")
        
        # Sum up all flow durations
        for section_key, flows in self.favorite["sequences"].items():
            print(f"Section: {section_key}")
            for flow in flows:
                flow_duration = flow.get("duration", 0)
                print(f"  Flow: {flow.get('name', 'NO NAME')} = {flow_duration} (type: {type(flow_duration)})")
                
                # Handle string durations like "5.5 minutes"
                if isinstance(flow_duration, str):
                    import re
                    numbers = re.findall(r'[\d.]+', flow_duration)
                    flow_duration = float(numbers[0]) if numbers else 0
                    print(f"    Converted to: {flow_duration}")
                
                total_duration += flow_duration
        
        print(f"Total calculated: {total_duration}")
        print("=================================")
        
        # Update the favorite's duration
        self.favorite["duration"] = f"{total_duration} minutes"
        
        # Find and update the General tab
        try:
            # Navigate up to find the main dialog
            dialog = self.parent()
            while dialog and not isinstance(dialog, QDialog):
                dialog = dialog.parent()
            
            if dialog:
                # Find the tab widget
                tab_widget = dialog.findChild(QTabWidget)
                if tab_widget:
                    general_tab = tab_widget.widget(0)  # General tab is first
                    if general_tab and hasattr(general_tab, 'refresh_duration'):
                        general_tab.refresh_duration()
                        print(f"Refreshed General tab with new duration: {self.favorite['duration']}")
        except Exception as e:
            print(f"Could not refresh General tab: {e}")

    def refresh_general_tab(self, dialog):
        """Refresh the General tab to show updated duration."""
        try:
            # Find the tab widget and General tab
            tab_widget = dialog.findChild(QTabWidget)
            if tab_widget:
                general_tab = tab_widget.widget(0)  # General tab is usually first
                if general_tab and hasattr(general_tab, 'refresh_duration'):
                    general_tab.refresh_duration()
        except Exception as e:
            print(f"Could not refresh General tab: {e}")

class History_Tab(QWidget):
    def __init__(self, favorite):
        super().__init__()
        self.favorite = favorite
        main_layout = QVBoxLayout()
        # Create scrollable area for favorites
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        header_label = QLabel("PRACTICE HISTORY")
        main_layout.addWidget(header_label)
        
        practice_history = self.favorite.get("practice_history", [])

        if len(practice_history) == 0:
            empty_message = QLabel("No practice sessions for this sequence yet!")
            scroll_layout.addWidget(empty_message)
            print(f"Zero Practice History. Message Displayed: {empty_message}")
        else:
            for session in self.favorite["practice_history"]:
                card_widget = QWidget()
                card_layout = QVBoxLayout()

                horizontal_widget = QWidget()
                horizontal_layout = QHBoxLayout()

                date_widget=QWidget()
                date_layout = QHBoxLayout()
                date_label = QLabel("DATE:")
                date_content = QLabel(session['date'])
                date_layout.addWidget(date_label)
                date_layout.addWidget(date_content)
                date_widget.setLayout(date_layout)


                rating_widget = QWidget()
                rating_layout = QHBoxLayout()
                rating_label = QLabel("RATING:")
                rating_content = QLabel(str(session['rating']))
                rating_layout.addWidget(rating_label)
                rating_layout.addWidget(rating_content)
                rating_widget.setLayout(rating_layout)
                

                horizontal_layout.addWidget(date_widget)
                horizontal_layout.addWidget(rating_widget)
                horizontal_widget.setLayout(horizontal_layout)

                notes_widget = QWidget()
                notes_layout=QVBoxLayout()
                notes_label = QLabel("NOTES:")
                notes_text = QTextEdit(session["notes"])
                notes_text.setReadOnly(True)
                notes_layout.addWidget(notes_label)
                notes_layout.addWidget(notes_text)
                notes_widget.setLayout(notes_layout)

                
                card_layout.addWidget(horizontal_widget)
                card_layout.addWidget(notes_widget)
                card_widget.setLayout(card_layout)
                scroll_layout.addWidget(card_widget)
            
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True) 
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

