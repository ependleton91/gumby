import logging
from typing import List, Optional, Callable, Any, Union
from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QApplication, QDialog, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QCursor, QPixmap, QIcon

logger = logging.getLogger(__name__)


def hide_widgets(widgets: List[QWidget]) -> None:
    #Hide a list of widgets safely.
    
    #Args:
    #    widgets: List of QWidget objects to hide
        
    #Example:
    #    hide_widgets([button1, button2, label1])
    for widget in widgets:
        if widget and isinstance(widget, QWidget):
            widget.setVisible(False)
            logger.debug(f"Hidden widget: {widget.objectName()}")


def show_widgets(widgets: List[QWidget]) -> None:
    #Show a list of widgets safely.
    
    #Args:
    #    widgets: List of QWidget objects to show
        
    #Example:
    #    show_widgets([button1, button2, label1])
    for widget in widgets:
        if widget and isinstance(widget, QWidget):
            widget.setVisible(True)
            logger.debug(f"Shown widget: {widget.objectName()}")


def enable_widgets(widgets: List[QWidget]) -> None:
    #Enable a list of widgets safely.
    
    #Args:
    #    widgets: List of QWidget objects to enable
    
    for widget in widgets:
        if widget and isinstance(widget, QWidget):
            widget.setEnabled(True)


def disable_widgets(widgets: List[QWidget]) -> None:
    #Disable a list of widgets safely.
    
    #Args:
    #    widgets: List of QWidget objects to disable
    
    for widget in widgets:
        if widget and isinstance(widget, QWidget):
            widget.setEnabled(False)


def toggle_widget_visibility(widget: QWidget) -> None:
    #Toggle widget visibility state.
    
    #Args:
    #    widget: Widget to toggle
        
    #Example:
    #    toggle_widget_visibility(advanced_options_panel)

    if widget and isinstance(widget, QWidget):
        widget.setVisible(not widget.isVisible())


def clear_layout(layout) -> None:
    #Remove all widgets from a layout safely.
    
    #Args:
    #    layout: QLayout to clear
        
    #Example:
    #    clear_layout(self.dynamic_content_layout)
    if layout is None:
        return
    
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


def show_error_message(parent: QWidget, title: str, message: str, 
                      details: str = None) -> None:
    
    #Show standardized error message dialog.
    
    #Args:
    #    parent: Parent widget for dialog
    #    title: Dialog title
    #    message: Main error message
    #    details: Optional detailed error information
        
    #Example:
    #    show_error_message(self, "Save Failed", "Could not save sequence", 
    #                      "File permissions error")
    
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()
    
    logger.error(f"Error dialog shown: {title} - {message}")


def show_warning_message(parent: QWidget, title: str, message: str) -> None:
    #Show standardized warning message dialog.
    
    #Args:
    #    parent: Parent widget for dialog
    #    title: Dialog title
    #    message: Warning message
        
    #Example:
    #    show_warning_message(self, "Unsaved Changes", 
    #                        "You have unsaved changes that will be lost")
    
    QMessageBox.warning(parent, title, message)
    logger.warning(f"Warning dialog shown: {title} - {message}")


def show_info_message(parent: QWidget, title: str, message: str) -> None:
    #Show standardized information message dialog.
    
    #Args:
    #    parent: Parent widget for dialog
    #    title: Dialog title
    #    message: Information message
        
    #Example:
    #    show_info_message(self, "Sequence Saved", 
    #                     "Your yoga sequence has been saved successfully")
    
    QMessageBox.information(parent, title, message)
    logger.info(f"Info dialog shown: {title} - {message}")


def show_success_message(parent: QWidget, title: str, message: str) -> None:
    #Show success message with custom styling.
    
    #Args:
    #    parent: Parent widget for dialog
    #    title: Dialog title
    #    message: Success message
    
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStyleSheet("QMessageBox { background-color: #d4edda; }")
    msg_box.exec()


def confirm_action(parent: QWidget, title: str, message: str, 
                  yes_text: str = "Yes", no_text: str = "No") -> bool:
    #Show confirmation dialog and return user choice.
    
    #Args:
    #    parent: Parent widget for dialog
    #    title: Dialog title
    #    message: Confirmation message
    #    yes_text: Text for affirmative button
    #    no_text: Text for negative button
        
    #Returns:
    #    True if user confirmed, False otherwise
        
    #Example:
    #    if confirm_action(self, "Delete Sequence", 
    #                     "Are you sure you want to delete this sequence?"):
    #        delete_sequence()

    result = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    
    confirmed = result == QMessageBox.StandardButton.Yes
    logger.info(f"Confirmation dialog: {title} - User {'confirmed' if confirmed else 'cancelled'}")
    return confirmed


def confirm_destructive_action(parent: QWidget, title: str, message: str, 
                             item_name: str = "") -> bool:
    #Show confirmation dialog for destructive actions with enhanced warning. 
        #Args:
        #    parent: Parent widget for dialog
        #    title: Dialog title
        #    message: Warning message
        #    item_name: Name of item being affected
            
        #Returns:
        #    True if user confirmed, False otherwise
    
    full_message = message
    if item_name:
        full_message += f"\n\nItem: {item_name}\n\nThis action cannot be undone."
    
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(full_message)
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
    )
    msg_box.setDefaultButton(QMessageBox.StandardButton.Cancel)
    
    # Style the Yes button to look dangerous
    yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
    if yes_button:
        yes_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
    
    result = msg_box.exec()
    return result == QMessageBox.StandardButton.Yes


def center_widget_on_screen(widget: QWidget) -> None:
    #Center widget on the primary screen.
    
    #Args:
    #    widget: Widget to center
        
    #Example:
    #    center_widget_on_screen(dialog)
    
    if not widget:
        return
    
    try:
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            widget_geometry = widget.geometry()
            
            x = (screen_geometry.width() - widget_geometry.width()) // 2
            y = (screen_geometry.height() - widget_geometry.height()) // 2
            
            widget.move(x, y)
            logger.debug(f"Centered widget at ({x}, {y})")
    except Exception as e:
        logger.error(f"Failed to center widget: {e}")


def set_widget_loading_state(widget: QWidget, is_loading: bool, 
                           loading_text: str = "Loading...") -> None:
    
    #Set widget to loading state with visual feedback.
    
    #Args:
    #    widget: Widget to modify
    #   is_loading: Whether widget is in loading state
    #   loading_text: Text to show during loading
        
    #Example:
    #    set_widget_loading_state(save_button, True, "Saving...")
    #    # ... perform save operation ...
    #    set_widget_loading_state(save_button, False)
    
    if not widget:
        return
    
    widget.setEnabled(not is_loading)
    
    if is_loading:
        widget.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        if hasattr(widget, 'setText'):
            widget._original_text = widget.text()
            widget.setText(loading_text)
    else:
        widget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        if hasattr(widget, 'setText') and hasattr(widget, '_original_text'):
            widget.setText(widget._original_text)
            delattr(widget, '_original_text')


def create_separator_line(orientation: str = "horizontal") -> QFrame:
#    Create a visual separator line.
    
#    Args:
#        orientation: "horizontal" or "vertical"
        
#    Returns:
#        QFrame configured as separator
        
#    Example:
#        separator = create_separator_line("horizontal")
#        layout.addWidget(separator)
    
    line = QFrame()
    
    if orientation.lower() == "horizontal":
        line.setFrameShape(QFrame.Shape.HLine)
    else:
        line.setFrameShape(QFrame.Shape.VLine)
    
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


# Convenience functions for common GUMBY operations
def show_pose_validation_errors(parent: QWidget, errors: List[str]) -> None:
    #Show pose validation errors in a formatted dialog.
    if not errors:
        return
    
    error_text = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in errors)
    show_error_message(parent, "Validation Errors", error_text)


def confirm_sequence_delete(parent: QWidget, sequence_name: str) -> bool:
    #Show confirmation for sequence deletion.
    return confirm_destructive_action(
        parent, 
        "Delete Sequence", 
        "Are you sure you want to delete this yoga sequence?",
        sequence_name
    )


def confirm_pose_delete(parent: QWidget, pose_name: str) -> bool:
    #Show confirmation for pose deletion.
    return confirm_destructive_action(
        parent,
        "Delete Pose",
        "Are you sure you want to delete this yoga pose?", 
        pose_name
    )


def show_save_success(parent: QWidget, item_type: str, item_name: str = "") -> None:
    #Show standardized save success message.
    message = f"{item_type} saved successfully"
    if item_name:
        message += f": {item_name}"
    
    show_success_message(parent, "Save Successful", message)