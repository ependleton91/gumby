import sqlite3
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized database management for GUMBY yoga app."""
    
    def __init__(self, db_path: Union[str, Path] = "app_data/gumby.db"):
        self.db_path = Path(db_path)
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            self._create_tables(conn)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create all necessary tables."""
        
        # Poses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS poses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                default_duration REAL NOT NULL,
                type TEXT NOT NULL,
                muscle_groups TEXT NOT NULL,  -- JSON array as string
                difficulty INTEGER NOT NULL,
                description TEXT,
                instructions TEXT,
                modifications TEXT,
                image_filename TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Flows table  
        conn.execute("""
            CREATE TABLE IF NOT EXISTS flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                duration REAL NOT NULL,
                category TEXT,
                style TEXT,  -- JSON array as string
                muscle_groups TEXT,  -- JSON array as string  
                difficulty INTEGER,
                energy_level TEXT,
                tags TEXT,  -- JSON array as string
                flow_data TEXT NOT NULL,  -- JSON string of the flow
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sequences table (for user-generated sequences)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                total_duration REAL NOT NULL,
                style TEXT,
                muscle_groups TEXT,  -- JSON array as string
                sequence_data TEXT NOT NULL,  -- JSON string of the sequence
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Favorites table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,  -- 'pose', 'flow', 'sequence'
                reference_id INTEGER,  -- ID of the favorited item
                favorite_data TEXT,  -- JSON string for complex favorites
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Practice sessions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS practice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sequence_name TEXT,
                duration_minutes REAL,
                rating INTEGER,  -- 1-5 stars
                notes TEXT,
                sequence_data TEXT  -- JSON string of what was practiced
            )
        """)
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_poses_name ON poses(name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_poses_difficulty ON poses(difficulty)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_flows_name ON flows(name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_flows_difficulty ON flows(difficulty)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_favorites_type ON favorites(type)")
        
        logger.info("Database tables created successfully")

# Global database manager instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get singleton database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# Utility functions for JSON handling in SQLite
def json_to_string(data: Any) -> str:
    """Convert Python object to JSON string for database storage."""
    if data is None:
        return "[]"
    if isinstance(data, list):
        return json.dumps(data)
    if isinstance(data, str):
        return data  # Assume already JSON
    return json.dumps([data])

def string_to_json(json_string: str) -> List:
    """Convert JSON string from database to Python list."""
    if not json_string:
        return []
    try:
        result = json.loads(json_string)
        return result if isinstance(result, list) else [result]
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON string: {json_string}")
        return []

# Pose database operations
def create_pose(pose_data: Dict[str, Any]) -> bool:
    """Insert a new pose into the database."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            conn.execute("""
                INSERT INTO poses (
                    name, default_duration, type, muscle_groups, 
                    difficulty, description, instructions, 
                    modifications, image_filename
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pose_data["name"],
                pose_data["default_duration"], 
                pose_data["type"],
                json_to_string(pose_data["muscle_groups"]),
                pose_data["difficulty"],
                pose_data.get("description", ""),
                pose_data.get("instructions", ""),
                pose_data.get("modifications", ""),
                pose_data.get("image_filename", "")
            ))
        logger.info(f"Created pose: {pose_data['name']}")
        return True
    except sqlite3.IntegrityError as e:
        logger.error(f"Pose already exists: {pose_data['name']}")
        return False
    except Exception as e:
        logger.error(f"Error creating pose: {e}")
        return False

def get_all_poses() -> Dict[str, Any]:
    """Get all poses in the format expected by existing code."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM poses ORDER BY name")
        rows = cursor.fetchall()
    
    poses = {}
    for row in rows:
        pose_key = row["name"].lower().replace(" ", "_").replace("-", "_")
        poses[pose_key] = {
            "name": row["name"],
            "default_duration": row["default_duration"],
            "type": row["type"], 
            "muscle_groups": string_to_json(row["muscle_groups"]),
            "difficulty": row["difficulty"],
            "description": row["description"] or "",
            "instructions": row["instructions"] or "",
            "modifications": row["modifications"] or "",
            "image_filename": row["image_filename"] or ""
        }
    
    return {"poses": poses}

def update_pose(pose_name: str, pose_data: Dict[str, Any]) -> bool:
    """Update an existing pose."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE poses SET 
                    name = ?, default_duration = ?, type = ?,
                    muscle_groups = ?, difficulty = ?, description = ?,
                    instructions = ?, modifications = ?, image_filename = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (
                pose_data["name"],
                pose_data["default_duration"],
                pose_data["type"], 
                json_to_string(pose_data["muscle_groups"]),
                pose_data["difficulty"],
                pose_data.get("description", ""),
                pose_data.get("instructions", ""),
                pose_data.get("modifications", ""),
                pose_data.get("image_filename", ""),
                pose_name
            ))
            
            if cursor.rowcount == 0:
                logger.warning(f"No pose found with name: {pose_name}")
                return False
                
        logger.info(f"Updated pose: {pose_name} -> {pose_data['name']}")
        return True
    except Exception as e:
        logger.error(f"Error updating pose: {e}")
        return False

def delete_pose(pose_name: str) -> bool:
    """Delete a pose from the database."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM poses WHERE name = ?", (pose_name,))
            
            if cursor.rowcount == 0:
                logger.warning(f"No pose found with name: {pose_name}")
                return False
                
        logger.info(f"Deleted pose: {pose_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting pose: {e}")
        return False

# Flow database operations
def create_flow(flow_data: Dict[str, Any]) -> bool:
    """Insert a new flow into the database."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            conn.execute("""
                INSERT INTO flows (
                    name, duration, category, style, muscle_groups,
                    difficulty, energy_level, tags, flow_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flow_data["name"],
                flow_data["duration"],
                flow_data.get("category", ""),
                json_to_string(flow_data.get("style", [])),
                json_to_string(flow_data.get("muscle_groups", [])),
                flow_data.get("difficulty", 1),
                flow_data.get("energy_level", ""),
                json_to_string(flow_data.get("tags", [])),
                json.dumps(flow_data.get("flow", []))
            ))
        logger.info(f"Created flow: {flow_data['name']}")
        return True
    except sqlite3.IntegrityError:
        logger.error(f"Flow already exists: {flow_data['name']}")
        return False
    except Exception as e:
        logger.error(f"Error creating flow: {e}")
        return False

def get_all_flows() -> Dict[str, Any]:
    """Get all flows in the format expected by existing code."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM flows ORDER BY name")
        rows = cursor.fetchall()
    
    flows = {}
    for row in rows:
        flow_key = row["name"].lower().replace(" ", "_").replace("-", "_")
        flows[flow_key] = {
            "name": row["name"],
            "duration": row["duration"],
            "category": row["category"] or "",
            "style": string_to_json(row["style"]),
            "muscle_groups": string_to_json(row["muscle_groups"]),
            "difficulty": row["difficulty"],
            "energy_level": row["energy_level"] or "",
            "tags": string_to_json(row["tags"]),
            "flow": json.loads(row["flow_data"]) if row["flow_data"] else []
        }
    
    return {"flowing_sequences": flows}

# Favorites database operations  
def get_all_favorites() -> Dict[str, Any]:
    """Get all favorites in the format expected by existing code."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM favorites ORDER BY created_at DESC")
        rows = cursor.fetchall()
    
    favorites = []
    for row in rows:
        favorite_data = json.loads(row["favorite_data"]) if row["favorite_data"] else {}
        favorite = {
            "name": row["name"],
            "type": row["type"],
            **favorite_data
        }
        favorites.append(favorite)
    
    return {"favorites": favorites}

def create_favorite(favorite_data: Dict[str, Any]) -> bool:
    """Add an item to favorites."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            conn.execute("""
                INSERT INTO favorites (name, type, reference_id, favorite_data)
                VALUES (?, ?, ?, ?)
            """, (
                favorite_data["name"],
                favorite_data.get("type", "sequence"),
                favorite_data.get("reference_id"),
                json.dumps(favorite_data)
            ))
        logger.info(f"Added to favorites: {favorite_data['name']}")
        return True
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        return False