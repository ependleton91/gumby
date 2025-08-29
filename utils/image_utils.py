import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt6.QtCore import Qt, QRect, QThread, QTimer, pyqtSignal, QObject
import threading
import time

logger = logging.getLogger(__name__)


class ImageCache:
    """Thread-safe LRU image cache with memory management."""
    
    def __init__(self, max_size: int = 100, max_memory_mb: int = 50):
        self._cache: Dict[str, Tuple[QPixmap, float]] = {}  # (pixmap, access_time)
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._lock = threading.RLock()
        self._current_memory = 0
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[QPixmap]:
        """Get image from cache with LRU tracking."""
        with self._lock:
            if key in self._cache:
                pixmap, _ = self._cache[key]
                # Update access time
                self._cache[key] = (pixmap, time.time())
                self.hits += 1
                return pixmap
            
            self.misses += 1
            return None
    
    def put(self, key: str, pixmap: QPixmap) -> None:
        """Store image with memory and size limits."""
        if pixmap.isNull():
            return
            
        with self._lock:
            # Calculate memory usage
            pixmap_bytes = pixmap.width() * pixmap.height() * 4  # RGBA
            
            # Remove existing entry if updating
            if key in self._cache:
                old_pixmap, _ = self._cache[key]
                old_bytes = old_pixmap.width() * old_pixmap.height() * 4
                self._current_memory -= old_bytes
            
            # Clean cache if needed
            self._cleanup_if_needed(pixmap_bytes)
            
            # Store new entry
            self._cache[key] = (pixmap, time.time())
            self._current_memory += pixmap_bytes
    
    def _cleanup_if_needed(self, new_bytes: int):
        """Remove least recently used items if limits exceeded."""
        while (len(self._cache) >= self.max_size or 
               self._current_memory + new_bytes > self.max_memory_bytes):
            
            if not self._cache:
                break
                
            # Find least recently used item
            lru_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            old_pixmap, _ = self._cache[lru_key]
            old_bytes = old_pixmap.width() * old_pixmap.height() * 4
            
            del self._cache[lru_key]
            self._current_memory -= old_bytes
    
    def clear(self) -> None:
        """Clear all cached images."""
        with self._lock:
            self._cache.clear()
            self._current_memory = 0
            self.hits = 0
            self.misses = 0
    
    def size(self) -> int:
        """Get number of cached images."""
        return len(self._cache)
    
    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache performance statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "entries": len(self._cache),
            "memory_mb": self._current_memory / (1024 * 1024),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": hit_rate
        }


class ImagePreloader(QObject):
    """Background thread for preloading common images."""
    
    image_loaded = pyqtSignal(str, QPixmap)  # key, pixmap
    
    def __init__(self, image_directory: Path):
        super().__init__()
        self.image_directory = Path(image_directory)
        self.preload_queue = []
        self.is_running = False
        
    def add_to_queue(self, pose_names: list):
        """Add pose names to preload queue."""
        for name in pose_names:
            filename = standardize_pose_name_to_filename(name)
            if filename not in self.preload_queue:
                self.preload_queue.append(filename)
    
    def start_preloading(self):
        """Start background preloading."""
        if self.is_running:
            return
            
        self.is_running = True
        threading.Thread(target=self._preload_worker, daemon=True).start()
    
    def _preload_worker(self):
        """Background worker that preloads images."""
        while self.preload_queue and self.is_running:
            filename = self.preload_queue.pop(0)
            image_path = self.image_directory / filename
            
            # Load image in background
            pixmap = load_image_from_path(image_path)
            if not pixmap.isNull():
                # Emit signal to main thread
                cache_key = f"{filename}:{self.image_directory}"
                self.image_loaded.emit(cache_key, pixmap)
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.01)
        
        self.is_running = False


# Global instances
_image_cache = ImageCache(max_size=200, max_memory_mb=100)
_preloader = None


def get_image_preloader(image_directory: Union[str, Path]) -> ImagePreloader:
    """Get or create image preloader for directory."""
    global _preloader
    if _preloader is None:
        _preloader = ImagePreloader(Path(image_directory))
        # Connect preloader to cache
        _preloader.image_loaded.connect(lambda key, pixmap: _image_cache.put(key, pixmap))
    return _preloader


def standardize_pose_name_to_filename(pose_name: str) -> str:
    """Convert pose name to standard filename format with caching."""
    if not pose_name:
        return "no_image.png"
    
    # Cache filename conversions to avoid repeated string operations
    if not hasattr(standardize_pose_name_to_filename, '_cache'):
        standardize_pose_name_to_filename._cache = {}
    
    if pose_name in standardize_pose_name_to_filename._cache:
        return standardize_pose_name_to_filename._cache[pose_name]
    
    # Convert to lowercase, replace spaces and apostrophes with underscores
    filename = pose_name.lower()
    filename = filename.replace(" ", "_").replace("'", "").replace("-", "_")
    
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
    
    result = f"{filename}.png"
    
    # Cache the result
    standardize_pose_name_to_filename._cache[pose_name] = result
    return result


def preload_common_poses(pose_names: list, image_directory: Union[str, Path]):
    """Preload commonly used pose images in background."""
    preloader = get_image_preloader(image_directory)
    preloader.add_to_queue(pose_names)
    preloader.start_preloading()


def load_pose_image(pose_name: str, image_directory: Union[str, Path], 
                   use_cache: bool = True, max_width: int = 0, max_height: int = 0) -> QPixmap:
    """Load pose image with optimized caching and optional sizing."""
    
    if not pose_name:
        return create_placeholder_image("No Pose", max_width or 200, max_height or 150)
    
    # Create cache key that includes sizing info
    size_key = f"_{max_width}x{max_height}" if max_width and max_height else ""
    cache_key = f"{pose_name}:{image_directory}{size_key}"
    
    # Check cache first
    if use_cache:
        cached_image = _image_cache.get(cache_key)
        if cached_image is not None:
            return cached_image
    
    # Generate filename and full path
    filename = standardize_pose_name_to_filename(pose_name)
    image_directory = Path(image_directory)
    image_path = image_directory / filename
    
    # Load image
    pixmap = load_image_from_path_optimized(image_path)
    
    if pixmap.isNull():
        # Try fallbacks
        fallback_names = ["no_image.png", "placeholder.png", "default_pose.png"]
        
        for fallback_name in fallback_names:
            fallback_path = image_directory / fallback_name
            pixmap = load_image_from_path_optimized(fallback_path)
            if not pixmap.isNull():
                break
    
    if pixmap.isNull():
        # Create placeholder
        pixmap = create_placeholder_image(pose_name, max_width or 200, max_height or 150)
    else:
        # Scale if requested
        if max_width and max_height:
            pixmap = scale_image_for_display_optimized(pixmap, max_width, max_height)
    
    # Cache the result
    if use_cache and not pixmap.isNull():
        _image_cache.put(cache_key, pixmap)
    
    return pixmap


def load_image_from_path_optimized(image_path: Union[str, Path]) -> QPixmap:
    """Optimized image loading with early validation."""
    image_path = Path(image_path)
    
    # Fast path checks
    if not image_path.exists():
        return QPixmap()
    
    # Check file size before attempting to load
    try:
        file_size = image_path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            logger.warning(f"Image file too large: {image_path}")
            return QPixmap()
        if file_size == 0:  # Empty file
            return QPixmap()
    except OSError:
        return QPixmap()
    
    # Quick extension check
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff'}
    if image_path.suffix.lower() not in valid_extensions:
        return QPixmap()
    
    try:
        pixmap = QPixmap(str(image_path))
        return pixmap
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return QPixmap()


def load_image_from_path(image_path: Union[str, Path]) -> QPixmap:
    """Backward compatibility wrapper."""
    return load_image_from_path_optimized(image_path)


def scale_image_for_display_optimized(pixmap: QPixmap, max_width: int, max_height: int, 
                                    smooth: bool = True) -> QPixmap:
    """Optimized image scaling with early returns."""
    if pixmap.isNull():
        return pixmap
    
    current_width = pixmap.width()
    current_height = pixmap.height()
    
    # Early return if already correct size
    if current_width <= max_width and current_height <= max_height:
        return pixmap
    
    # Calculate if scaling is actually needed
    width_ratio = max_width / current_width
    height_ratio = max_height / current_height
    scale_ratio = min(width_ratio, height_ratio)
    
    # If scaling would be minimal, skip it
    if scale_ratio > 0.95:
        return pixmap
    
    # Use fast scaling for small images or when smooth is False
    transformation = (Qt.TransformationMode.SmoothTransformation 
                     if smooth and (current_width > 200 or current_height > 200)
                     else Qt.TransformationMode.FastTransformation)
    
    return pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, transformation)


def scale_image_for_display(pixmap: QPixmap, max_width: int, max_height: int, 
                           smooth: bool = True) -> QPixmap:
    """Backward compatibility wrapper."""
    return scale_image_for_display_optimized(pixmap, max_width, max_height, smooth)


def create_placeholder_image(pose_name: str, width: int = 200, height: int = 150, 
                           background_color: QColor = None) -> QPixmap:
    """Create placeholder image with caching for common sizes."""
    
    # Cache common placeholders
    cache_key = f"placeholder_{width}x{height}_{hash(pose_name)}"
    cached = _image_cache.get(cache_key)
    if cached is not None:
        return cached
    
    if background_color is None:
        background_color = QColor(220, 220, 220)
    
    pixmap = QPixmap(width, height)
    pixmap.fill(background_color)
    
    # Optimize text rendering for small placeholders
    if width < 150 or height < 100:
        # Skip text for very small placeholders to save processing
        _image_cache.put(cache_key, pixmap)
        return pixmap
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Scale font size based on image size
    font_size = min(12, max(8, min(width, height) // 15))
    font = QFont()
    font.setPointSize(font_size)
    font.setBold(True)
    painter.setFont(font)
    
    painter.setPen(QColor(100, 100, 100))
    
    # Truncate long names
    display_name = pose_name[:50] + "..." if len(pose_name) > 50 else pose_name
    
    text_rect = QRect(5, 5, width - 10, height - 10)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, display_name)
    
    painter.end()
    
    # Cache the placeholder
    _image_cache.put(cache_key, pixmap)
    return pixmap


def validate_image_file(file_path: Union[str, Path]) -> bool:
    """Fast image file validation."""
    file_path = Path(file_path)
    
    # Fast checks first
    if not file_path.exists() or not file_path.is_file():
        return False
    
    # Extension check
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff'}
    if file_path.suffix.lower() not in valid_extensions:
        return False
    
    # Size check
    try:
        file_size = file_path.stat().st_size
        if file_size == 0 or file_size > 50 * 1024 * 1024:  # 0 bytes or > 50MB
            return False
    except OSError:
        return False
    
    return True


def clear_image_cache() -> None:
    """Clear the global image cache."""
    _image_cache.clear()
    # Clear filename cache too
    if hasattr(standardize_pose_name_to_filename, '_cache'):
        standardize_pose_name_to_filename._cache.clear()
    logger.info("Cleared image cache")


def get_cache_stats() -> Dict[str, Union[int, float]]:
    """Get detailed cache statistics."""
    return _image_cache.get_stats()


# Optimized convenience functions
def load_thumbnail_image(pose_name: str, image_directory: Union[str, Path]) -> QPixmap:
    """Load pose image sized for thumbnails (150x150) with caching."""
    return load_pose_image(pose_name, image_directory, use_cache=True, max_width=150, max_height=150)


def load_preview_image(pose_name: str, image_directory: Union[str, Path]) -> QPixmap:
    """Load pose image sized for preview (400x300) with caching."""
    return load_pose_image(pose_name, image_directory, use_cache=True, max_width=400, max_height=300)


def load_carousel_image(pose_name: str, image_directory: Union[str, Path]) -> QPixmap:
    """Load pose image sized for carousel (100x100) with caching."""
    return load_pose_image(pose_name, image_directory, use_cache=True, max_width=100, max_height=100)


# Batch loading for UI initialization
def preload_ui_images(pose_names: list, image_directory: Union[str, Path], sizes: list = None):
    """Preload multiple images for UI in background."""
    if sizes is None:
        sizes = [(150, 150), (400, 300), (100, 100)]  # thumbnail, preview, carousel
    
    def background_loader():
        for pose_name in pose_names:
            for width, height in sizes:
                # This will populate the cache
                load_pose_image(pose_name, image_directory, max_width=width, max_height=height)
                time.sleep(0.001)  # Small delay to not block UI
    
    threading.Thread(target=background_loader, daemon=True).start()


# Memory management
def optimize_cache_for_memory():
    """Reduce cache memory usage by clearing least important entries."""
    stats = get_cache_stats()
    if stats["memory_mb"] > 75:  # If using more than 75MB
        # Clear half the cache, keeping most recently used
        current_size = _image_cache.size()
        target_size = current_size // 2
        
        # The LRU cleanup will handle this automatically when we try to add new items
        logger.info(f"Cache memory usage high ({stats['memory_mb']:.1f}MB), will cleanup on next additions")