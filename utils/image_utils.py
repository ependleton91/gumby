import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt6.QtCore import Qt, QRect

logger = logging.getLogger(__name__)


class ImageCache:
    #Simple image cache to avoid reloading the same images.
    
    def __init__(self, max_size: int = 100):
        self._cache: Dict[str, QPixmap] = {}
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[QPixmap]:
        #Get image from cache.
        return self._cache.get(key)
    
    def put(self, key: str, pixmap: QPixmap) -> None:
        #Store image in cache with size limit
        if len(self._cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = pixmap
    
    def clear(self) -> None:
        #Clear all cached images.
        self._cache.clear()
    
    def size(self) -> int:
        #Get number of cached images.
        return len(self._cache)


# Global image cache instance
_image_cache = ImageCache()


def standardize_pose_name_to_filename(pose_name: str) -> str:
    #Convert pose name to standard filename format.
    
    #Args:
    #    pose_name: Human-readable pose name
        
    #Returns:
    #    Standardized filename with .png extension
        
    #Example:
    #    standardize_pose_name_to_filename("Mountain Pose") -> "mountain_pose.png"
    #    standardize_pose_name_to_filename("Child's Pose") -> "childs_pose.png"
    if not pose_name:
        return "no_image.png"
    
    # Convert to lowercase, replace spaces and apostrophes with underscores
    filename = pose_name.lower()
    filename = filename.replace(" ", "_")
    filename = filename.replace("'", "")
    filename = filename.replace("-", "_")
    
    # Remove any other special characters
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789_"
    filename = "".join(c for c in filename if c in allowed_chars)
    
    # Remove duplicate underscores
    while "__" in filename:
        filename = filename.replace("__", "_")
    
    # Remove leading/trailing underscores
    filename = filename.strip("_")
    
    if not filename:
        filename = "no_image"
    
    return f"{filename}.png"


def load_pose_image(pose_name: str, image_directory: Union[str, Path], 
                   use_cache: bool = True) -> QPixmap:
    #Load pose image with standardized naming and fallback handling.
    
    #Args:
    #    pose_name: Name of the pose
    #    image_directory: Directory containing pose images
    #    use_cache: Whether to use image cache
        
    #Returns:
    #    QPixmap with the loaded image or fallback
        
    #Example:
    #    pixmap = load_pose_image("Mountain Pose", "assets/images/poses")
    
    if not pose_name:
        return create_placeholder_image("No Pose")
    
    # Check cache first
    cache_key = f"{pose_name}:{image_directory}"
    if use_cache:
        cached_image = _image_cache.get(cache_key)
        if cached_image is not None:
            return cached_image
    
    # Generate filename and full path
    filename = standardize_pose_name_to_filename(pose_name)
    image_directory = Path(image_directory)
    image_path = image_directory / filename
    
    # Try to load the specific image
    pixmap = load_image_from_path(image_path)
    
    if pixmap.isNull():
        # Try common fallback names
        fallback_names = ["no_image.png", "placeholder.png", "default_pose.png"]
        
        for fallback_name in fallback_names:
            fallback_path = image_directory / fallback_name
            pixmap = load_image_from_path(fallback_path)
            if not pixmap.isNull():
                break
    
    if pixmap.isNull():
        # Create programmatic placeholder as last resort
        pixmap = create_placeholder_image(pose_name)
        logger.warning(f"Created placeholder for {pose_name} - no image file found")
    
    # Cache the result
    if use_cache:
        _image_cache.put(cache_key, pixmap)
    
    return pixmap


def load_image_from_path(image_path: Union[str, Path]) -> QPixmap:
    #Load image from specific file path.
    
    #Args:
    #    image_path: Full path to image file
        
    #Returns:
    #    QPixmap (may be null if loading failed)
    image_path = Path(image_path)
    
    if not image_path.exists():
        logger.debug(f"Image file does not exist: {image_path}")
        return QPixmap()
    
    if not validate_image_file(image_path):
        logger.warning(f"Invalid image file format: {image_path}")
        return QPixmap()
    
    try:
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            logger.debug(f"Successfully loaded image: {image_path}")
        else:
            logger.warning(f"Failed to load image: {image_path}")
        return pixmap
        
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return QPixmap()


def scale_image_for_display(pixmap: QPixmap, max_width: int, max_height: int, 
                           smooth: bool = True) -> QPixmap:
    #Scale image maintaining aspect ratio within given dimensions.
    
    #Args:
    #    pixmap: Original image
    #    max_width: Maximum width
    #    max_height: Maximum height
    #    smooth: Use smooth scaling (slower but better quality)
        
    #Returns:
    #    Scaled QPixmap
        
    #Example:
    #    scaled = scale_image_for_display(original_image, 300, 200)
    if pixmap.isNull():
        return pixmap
    
    if pixmap.width() <= max_width and pixmap.height() <= max_height:
        return pixmap
    
    transformation = Qt.TransformationMode.SmoothTransformation if smooth else Qt.TransformationMode.FastTransformation
    
    return pixmap.scaled(
        max_width, max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        transformation
    )


def create_placeholder_image(pose_name: str, width: int = 200, height: int = 150, 
                           background_color: QColor = None) -> QPixmap:
    #Create a placeholder image with pose name text.
    
    #Args:
    #    pose_name: Text to display on placeholder
    #    width: Image width
    #    height: Image height
    #    background_color: Background color (default: light gray)
        
    #Returns:
    #    QPixmap with placeholder
    
    if background_color is None:
        background_color = QColor(220, 220, 220)  # Light gray
    
    pixmap = QPixmap(width, height)
    pixmap.fill(background_color)
    
    # Add text
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Set up font
    font = QFont()
    font.setPointSize(12)
    font.setBold(True)
    painter.setFont(font)
    
    # Set text color
    painter.setPen(QColor(100, 100, 100))  # Dark gray
    
    # Draw text centered
    text_rect = QRect(10, 10, width - 20, height - 20)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, pose_name)
    
    painter.end()
    
    return pixmap


def validate_image_file(file_path: Union[str, Path]) -> bool:

    #Check if file is a valid image format.
    
    #Args:
    #    file_path: Path to image file
        
    #Returns:
    #    True if file appears to be a valid image

    file_path = Path(file_path)
    
    if not file_path.exists():
        return False
    
    if not file_path.is_file():
        return False
    
    # Check file extension
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff'}
    if file_path.suffix.lower() not in valid_extensions:
        return False
    
    # Check file size (avoid huge files)
    try:
        file_size = file_path.stat().st_size
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            logger.warning(f"Image file too large: {file_path} ({file_size} bytes)")
            return False
    except:
        return False
    
    return True


def clear_image_cache() -> None:
    """Clear the global image cache."""
    _image_cache.clear()
    logger.info("Cleared image cache")


# Convenience functions for specific image sizes used in GUMBY
def load_thumbnail_image(pose_name: str, image_directory: Union[str, Path]) -> QPixmap:
    """Load pose image sized for thumbnails (150x150)."""
    pixmap = load_pose_image(pose_name, image_directory)
    return scale_image_for_display(pixmap, 150, 150)


def load_preview_image(pose_name: str, image_directory: Union[str, Path]) -> QPixmap:
    """Load pose image sized for preview (400x300)."""
    pixmap = load_pose_image(pose_name, image_directory)
    return scale_image_for_display(pixmap, 400, 300)
