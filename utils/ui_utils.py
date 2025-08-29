import logging
from typing import List, Optional, Callable, Any, Union, Dict
from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QApplication, QDialog, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCursor, QPixmap, QIcon
import weakref

logger = logging.getLogger(__name__)

# Cache for message boxes to avoid creating identical dialogs
_message_box_cache: Dict[str, QMessageBox] = {}

def hide_widgets(widgets: List[QWidget], animated: bool = False) -> None:
    """Hide a list of widgets safely with optional animation.
    
    Args:
        widgets: List of QWidget objects to hide
        animated: Whether to use fade-out animation
        
    Example:
        hide_widgets([button1, button2, label1])
        hide_widgets([panel], animated=True)
    """
    valid_widgets = [w for w in widgets if w and isinstance(w, QWidget)]
    
    if not animated:
        # Fast path - no animation
        for widget in valid_widgets:
            widget.setVisible(False)
            logger.debug(f"Hidden widget: {widget.objectName()}")
    else:
        # Animated fade out
        for widget in valid_widgets:
            fade_out_widget(widget)

def show_widgets(widgets: List[QWidget], animated: bool = False) -> None:
    """Show a list of widgets safely with optional animation.
    
    Args:
        widgets: List of QWidget objects to show
        animated: Whether to use fade-in animation
        
    Example:
        show_widgets([button1, button2, label1])
        show_widgets([panel], animated=True)
    """
    valid_widgets = [w for w in widgets if w and isinstance(w, QWidget)]
    
    if not animated:
        # Fast path - no animation
        for widget in valid_widgets:
            widget.setVisible(True)
            logger.debug(f"Shown widget: {widget.objectName()}")
    else:
        # Animated fade in
        for widget in valid_widgets:
            fade_in_widget(widget)

def batch_widget_operations(widgets: List[QWidget], operation: str, **kwargs) -> None:
    """Perform batch operations on widgets for better performance.
    
    Args:
        widgets: List of widgets to operate on
        operation: 'hide', 'show', 'enable', 'disable'
        **kwargs: Additional arguments (e.g., animated=True)
    """
    # Filter valid widgets once
    valid_widgets = [w for w in widgets if w and isinstance(w, QWidget)]
    
    if not valid_widgets:
        return
    
    # Disable updates during batch operation for performance
    for widget in valid_widgets:
        if hasattr(widget, 'setUpdatesEnabled'):
            widget.setUpdatesEnabled(False)
    
    try:
        if operation == 'hide':
            hide_widgets(valid_widgets, **kwargs)
        elif operation == 'show':
            show_widgets(valid_widgets, **kwargs)
        elif operation == 'enable':
            enable_widgets(valid_widgets)
        elif operation == 'disable':
            disable_widgets(valid_widgets)
    finally:
        # Re-enable updates
        for widget in valid_widgets:
            if hasattr(widget, 'setUpdatesEnabled'):
                widget.setUpdatesEnabled(True)

def enable_widgets(widgets: List[QWidget]) -> None:
    """Enable a list of widgets safely."""
    for widget in widgets:
        if widget and isinstance(widget, QWidget):
            widget.setEnabled(True)

def disable_widgets(widgets: List[QWidget]) -> None:
    """Disable a list of widgets safely."""
    for widget in widgets:
        if widget and isinstance(widget, QWidget):
            widget.setEnabled(False)

def toggle_widget_visibility(widget: QWidget, animated: bool = False) -> None:
    """Toggle widget visibility state with optional animation."""
    if widget and isinstance(widget, QWidget):
        if widget.isVisible():
            hide_widgets([widget], animated)
        else:
            show_widgets([widget], animated)

def clear_layout(layout, delete_widgets: bool = True) -> None:
    """Remove all widgets from a layout safely with performance optimization.
    
    Args:
        layout: QLayout to clear
        delete_widgets: Whether to delete widgets or just remove them
    """
    if layout is None:
        return
    
    # Batch collect all items first
    items_to_remove = []
    while layout.count():
        items_to_remove.append(layout.takeAt(0))
    
    # Process removals
    for child in items_to_remove:
        if child.widget() and delete_widgets:
            child.widget().deleteLater()

def fade_out_widget(widget: QWidget, duration: int = 250) -> None:
    """Fade out a widget with animation."""
    if not widget:
        return
        
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # Hide widget when animation finishes
    animation.finished.connect(lambda: widget.setVisible(False))
    animation.start()

def fade_in_widget(widget: QWidget, duration: int = 250) -> None:
    """Fade in a widget with animation."""
    if not widget:
        return
        
    widget.setVisible(True)
    
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.InCubic)
    
    animation.start()

# Optimized message box functions with caching
def show_error_message(parent: QWidget, title: str, message: str, 
                      details: str = None, cache_key: str = None) -> None:
    """Show error message with optional caching for repeated dialogs."""
    
    # Use cache if key provided and dialog exists
    if cache_key and cache_key in _message_box_cache:
        msg_box = _message_box_cache[cache_key]
        msg_box.setText(message)
        if details:
            msg_box.setDetailedText(details)
        msg_box.exec()
        logger.error(f"Error dialog shown (cached): {title} - {message}")
        return
    
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    # Cache if key provided
    if cache_key:
        _message_box_cache[cache_key] = msg_box
    
    msg_box.exec()
    logger.error(f"Error dialog shown: {title} - {message}")

def show_warning_message(parent: QWidget, title: str, message: str) -> None:
    """Show warning message dialog."""
    QMessageBox.warning(parent, title, message)
    logger.warning(f"Warning dialog shown: {title} - {message}")

def show_info_message(parent: QWidget, title: str, message: str) -> None:
    """Show information message dialog."""
    QMessageBox.information(parent, title, message)
    logger.info(f"Info dialog shown: {title} - {message}")

def show_success_message(parent: QWidget, title: str, message: str, 
                        auto_close: bool = False, timeout: int = 3000) -> None:
    """Show success message with optional auto-close.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Success message
        auto_close: Whether to auto-close the dialog
        timeout: Timeout in milliseconds for auto-close
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStyleSheet("QMessageBox { background-color: #d4edda; }")
    
    if auto_close:
        # Auto-close after timeout
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(msg_box.accept)
        timer.start(timeout)
        
        # Store timer reference so it doesn't get garbage collected
        msg_box._timer = timer
    
    msg_box.exec()

def confirm_action(parent: QWidget, title: str, message: str, 
                  yes_text: str = "Yes", no_text: str = "No",
                  default_yes: bool = False) -> bool:
    """Show confirmation dialog with customizable default.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Confirmation message
        yes_text: Text for affirmative button
        no_text: Text for negative button
        default_yes: Whether Yes should be the default button
    """
    result = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes if default_yes else QMessageBox.StandardButton.No
    )
    
    confirmed = result == QMessageBox.StandardButton.Yes
    logger.info(f"Confirmation dialog: {title} - User {'confirmed' if confirmed else 'cancelled'}")
    return confirmed

def confirm_destructive_action(parent: QWidget, title: str, message: str, 
                             item_name: str = "", require_double_confirm: bool = False) -> bool:
    """Show confirmation for destructive actions with optional double confirmation."""
    
    full_message = message
    if item_name:
        full_message += f"\n\nItem: {item_name}\n\nThis action cannot be undone."
    
    if require_double_confirm:
        full_message += "\n\nThis is a permanent action. Are you absolutely sure?"
    
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
        if require_double_confirm:
            yes_button.setText("Delete Permanently")
    
    result = msg_box.exec()
    confirmed = result == QMessageBox.StandardButton.Yes
    
    # Double confirmation if requested
    if confirmed and require_double_confirm:
        return confirm_action(parent, "Final Confirmation", 
                            f"Last chance: Really delete {item_name}?", 
                            "DELETE", "Cancel")
    
    return confirmed

def center_widget_on_screen(widget: QWidget) -> None:
    """Center widget on the primary screen with error handling."""
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

def center_widget_on_parent(widget: QWidget, parent: QWidget) -> None:
    """Center widget relative to parent widget."""
    if not widget or not parent:
        return
    
    try:
        parent_geometry = parent.geometry()
        widget_geometry = widget.geometry()
        
        x = parent_geometry.x() + (parent_geometry.width() - widget_geometry.width()) // 2
        y = parent_geometry.y() + (parent_geometry.height() - widget_geometry.height()) // 2
        
        widget.move(x, y)
    except Exception as e:
        logger.error(f"Failed to center widget on parent: {e}")

def set_widget_loading_state(widget: QWidget, is_loading: bool, 
                           loading_text: str = "Loading...", 
                           disable_parent: bool = False) -> None:
    """Set widget loading state with optional parent disabling."""
    if not widget:
        return
    
    widget.setEnabled(not is_loading)
    
    # Optionally disable parent to prevent all interactions
    if disable_parent and widget.parent():
        widget.parent().setEnabled(not is_loading)
    
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

def create_separator_line(orientation: str = "horizontal", 
                         thickness: int = 1, color: str = "#cccccc") -> QFrame:
    """Create a visual separator line with customizable appearance."""
    line = QFrame()
    
    if orientation.lower() == "horizontal":
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(thickness)
    else:
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedWidth(thickness)
    
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setStyleSheet(f"QFrame {{ color: {color}; background-color: {color}; }}")
    return line

# Enhanced GUMBY-specific functions
def show_pose_validation_errors(parent: QWidget, errors: List[str]) -> None:
    """Show pose validation errors in a formatted dialog."""
    if not errors:
        return
    
    error_text = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in errors)
    show_error_message(parent, "Validation Errors", error_text)

def confirm_sequence_delete(parent: QWidget, sequence_name: str) -> bool:
    """Show confirmation for sequence deletion."""
    return confirm_destructive_action(
        parent, 
        "Delete Sequence", 
        "Are you sure you want to delete this yoga sequence?",
        sequence_name,
        require_double_confirm=True
    )

def confirm_pose_delete(parent: QWidget, pose_name: str) -> bool:
    """Show confirmation for pose deletion."""
    return confirm_destructive_action(
        parent,
        "Delete Pose",
        "Are you sure you want to delete this yoga pose?", 
        pose_name
    )

def show_save_success(parent: QWidget, item_type: str, item_name: str = "", 
                     auto_close: bool = True) -> None:
    """Show standardized save success message with auto-close."""
    message = f"{item_type} saved successfully"
    if item_name:
        message += f": {item_name}"
    
    show_success_message(parent, "Save Successful", message, auto_close=auto_close)

# Progress dialog for long operations
class ProgressDialog(QDialog):
    """Progress dialog for long-running operations with cancellation support."""
    
    cancelled = pyqtSignal()
    
    def __init__(self, parent: QWidget, title: str, message: str = "", 
                 can_cancel: bool = True, max_value: int = 0):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout()
        
        if message:
            self.message_label = QLabel(message)
            self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.message_label)
        
        self.progress_bar = QProgressBar()
        if max_value > 0:
            self.progress_bar.setRange(0, max_value)
        else:
            self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        if can_cancel:
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self.cancel_operation)
            layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)
        center_widget_on_parent(self, parent)
    
    def update_progress(self, value: int, message: str = None):
        """Update progress value and optional message."""
        self.progress_bar.setValue(value)
        if message and hasattr(self, 'message_label'):
            self.message_label.setText(message)
    
    def cancel_operation(self):
        """Handle cancel button click."""
        self.cancelled.emit()
        self.reject()

# Memory management
def clear_ui_caches():
    """Clear UI-related caches to free memory."""
    global _message_box_cache
    _message_box_cache.clear()

def get_ui_cache_stats() -> Dict[str, int]:
    """Get UI cache statistics."""
    return {
        "message_box_cache_size": len(_message_box_cache)
    }