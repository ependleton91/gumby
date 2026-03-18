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
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
##Any new tables or changes to columns should be updated here if added in db
    def _create_tables(self, conn: sqlite3.Connection):
        """Create all normalized tables without JSON dependencies."""
        
        # Core entities
        conn.execute("""
            CREATE TABLE IF NOT EXISTS poses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                default_duration REAL NOT NULL,
                type TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                description TEXT DEFAULT '',
                instructions TEXT DEFAULT '',
                modifications TEXT DEFAULT '',
                image_filename TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                duration REAL NOT NULL,
                category TEXT DEFAULT '',
                difficulty INTEGER DEFAULT 1,
                energy_level TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                total_duration REAL NOT NULL,
                difficulty INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lookup tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS muscle_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS yoga_styles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        
        # Favorites system
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorite_poses (
                favorite_id INTEGER REFERENCES favorites(id) ON DELETE CASCADE,
                pose_id INTEGER REFERENCES poses(id) ON DELETE CASCADE,
                PRIMARY KEY (favorite_id, pose_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorite_flows (
                favorite_id INTEGER REFERENCES favorites(id) ON DELETE CASCADE,
                flow_id INTEGER REFERENCES flows(id) ON DELETE CASCADE,
                PRIMARY KEY (favorite_id, flow_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorite_sequences (
                favorite_id INTEGER REFERENCES favorites(id) ON DELETE CASCADE,
                sequence_id INTEGER REFERENCES sequences(id) ON DELETE CASCADE,
                PRIMARY KEY (favorite_id, sequence_id)
            )
        """)
        
        # Practice sessions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS practice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_id INTEGER REFERENCES sequences(id),
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes REAL,
                rating INTEGER,
                notes TEXT
            )
        """)
        
        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_poses_name ON poses(name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_flows_name ON flows(name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sequences_name ON sequences(name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_flow_poses_order ON flow_poses(flow_id, sequence_order)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sequence_flows_order ON sequence_flows(sequence_id, section_type, sequence_order)")
        
        logger.info("Normalized database tables created successfully")

# Global database manager instance
_db_manager = None

#DB manager is used to manage database connections and operations between different parts of the app
def get_db_manager() -> DatabaseManager:
    """Get singleton database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

# Helper functions for lookup tables
def ensure_muscle_group_exists(name: str) -> int:
    """Get or create muscle group, return ID."""
    db = get_db_manager()
    with db.get_connection() as conn:
        # Try to get existing
        cursor = conn.execute("SELECT id FROM muscle_groups WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            return result["id"]
        
        # Create new
        cursor = conn.execute("INSERT INTO muscle_groups (name) VALUES (?)", (name,))
        return cursor.lastrowid

def ensure_yoga_style_exists(name: str) -> int:
    """Get or create yoga style, return ID."""
    db = get_db_manager()
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT id FROM yoga_styles WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            return result["id"]
        
        cursor = conn.execute("INSERT INTO yoga_styles (name) VALUES (?)", (name,))
        return cursor.lastrowid

def get_pose_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get pose by name with muscle groups."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT p.*
            FROM poses p
            WHERE p.name = ?
            GROUP BY p.id
        """, (name,))

        row = cursor.fetchone()
        if not row:
            return None
        
        #Look up name for each muscle group id, replace with name
        muscle_groups = row["muscle_groups"].split(",") if row["muscle_groups"] else []
        for id in muscle_groups:
            cursor = conn.execute("""
                SELECT name 
                FROM muscle_groups
                WHERE id = ?
            """, (id,))
            muscle_group = cursor.fetchone()
            if muscle_group:
                muscle_groups.replace(id, muscle_group["name"])

        return {
            "id": row["id"],
            "name": row["name"],
            "default_duration": row["default_duration"],
            "type": row["type"],
            "muscle_groups": muscle_groups,
            "difficulty": row["difficulty"],
            "description": row["description"] or "",
            "instructions": row["instructions"] or "",
            "modifications": row["modifications"] or "",
            "image_filename": row["image_filename"] or ""
        }

# POSE OPERATIONS
def create_pose(pose_data: Dict[str, Any]) -> bool:
    """Create pose with normalized muscle group relationships."""
    db = get_db_manager()
    try:
        with db.get_connection() as conn:
            # Insert pose
            cursor = conn.execute("""
                INSERT INTO poses (name, default_duration, type, difficulty, 
                                 description, instructions, modifications, image_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pose_data["name"], pose_data["default_duration"], pose_data["type"],
                pose_data["difficulty"], pose_data.get("description", ""),
                pose_data.get("instructions", ""), pose_data.get("modifications", ""),
                pose_data.get("image_filename", "")
            ))
            
            pose_id = cursor.lastrowid
            muscle_ids = []

            # Grab Muscle ID's For each Muscle in Muscle Groups
            for muscle_name in pose_data.get("muscle_groups", []):
                muscle_id = ensure_muscle_group_exists(muscle_name)
                muscle_ids.append(muscle_id)
            #Add muscle groups to pose as array of muscle ids
            conn.execute(
                "UPDATE poses SET muscle_groups = ? WHERE id = ?",
                 (muscle_ids, pose_id)
                )
        
        logger.info(f"Created pose: {pose_data['name']}")
        return True
    except sqlite3.IntegrityError:
        logger.error(f"Pose already exists: {pose_data['name']}")
        return False
    except Exception as e:
        logger.error(f"Error creating pose: {e}")
        return False

def get_all_poses() -> List[Dict[str, Any]]:
    """Get all poses with muscle groups from normalized tables."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT p.*
            FROM poses p
            GROUP BY p.id
            ORDER BY p.name
        """)
        
        poses = []
        for row in cursor.fetchall():

            #Look up name for each muscle group id, replace with name
            muscle_groups = row["muscle_groups"].split(",") if row["muscle_groups"] else []
            for id in muscle_groups:
                cursor = conn.execute("""
                    SELECT name 
                    FROM muscle_groups
                    WHERE id = ?
                """, (id,))
                muscle_group = cursor.fetchone()
                if muscle_group:
                    muscle_groups.replace(id, muscle_group["name"])

            poses.append({
                "id": row["id"],
                "name": row["name"],
                "default_duration": row["default_duration"],
                "type": row["type"],
                "muscle_groups": muscle_groups,
                "difficulty": row["difficulty"],
                "description": row["description"] or "",
                "instructions": row["instructions"] or "",
                "modifications": row["modifications"] or "",
                "image_filename": row["image_filename"] or ""
            })
        
        return poses

def update_pose(pose_name: str, pose_data: Dict[str, Any]) -> bool:
    """Update an existing pose with normalized muscle groups."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            # Get pose ID
            cursor = conn.execute("SELECT id FROM poses WHERE name = ?", (pose_name,))
            result = cursor.fetchone()
            if not result:
                logger.warning(f"No pose found with name: {pose_name}")
                return False
            
            pose_id = result["id"]

            muscle_ids = []
            # Grab Muscle ID's For each Muscle in Muscle Groups
            for muscle_name in pose_data.get("muscle_groups", []):
                muscle_id = ensure_muscle_group_exists(muscle_name)
                muscle_ids.append(muscle_id)
            
            # Update pose
            cursor = conn.execute("""
                UPDATE poses SET 
                    name = ?, default_duration = ?, type = ?, difficulty = ?,
                    description = ?, instructions = ?, modifications = ?, 
                    image_filename = ?, updated_at = CURRENT_TIMESTAMP, muscle_groups = ?
                WHERE id = ?
            """, (
                pose_data["name"], pose_data["default_duration"], pose_data["type"],
                pose_data["difficulty"], pose_data.get("description", ""),
                pose_data.get("instructions", ""), pose_data.get("modifications", ""),
                pose_data.get("image_filename", ""), muscle_ids, pose_id
            ))

        logger.info(f"Updated pose: {pose_name} -> {pose_data['name']}")
        return True
    except Exception as e:
        logger.error(f"Error updating pose: {e}")
        return False

def delete_pose(pose_name: str) -> bool:
    """Delete a pose and all its relationships."""
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

# FLOW OPERATIONS
def create_flow(flow_data: Dict[str, Any]) -> bool:
    """Create flow with normalized relationships."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            # Insert flow metadata
            cursor = conn.execute("""
                INSERT INTO flows (name, duration, category, difficulty, energy_level)
                VALUES (?, ?, ?, ?, ?)
            """, (
                flow_data["name"], flow_data.get("duration", 0),
                flow_data.get("category", ""), flow_data.get("difficulty", 1),
                flow_data.get("energy_level", "")
            ))
            
            flow_id = cursor.lastrowid
            
            # Link styles
            for style_name in flow_data.get("style", []):
                style_id = ensure_yoga_style_exists(style_name)
                conn.execute(
                    "INSERT INTO flow_styles (flow_id, style_id) VALUES (?, ?)",
                    (flow_id, style_id)
                )
            
            # Link muscle groups
            for muscle_name in flow_data.get("muscle_groups", []):
                muscle_id = ensure_muscle_group_exists(muscle_name)
                conn.execute(
                    "INSERT INTO flow_muscle_groups (flow_id, muscle_group_id) VALUES (?, ?)",
                    (flow_id, muscle_id)
                )
            
            # Link poses in sequence
            for order, pose_info in enumerate(flow_data.get("flow", [])):
                pose_name = pose_info.get("name", "")
                pose_duration = pose_info.get("duration")
                
                # Get pose ID by name
                pose_cursor = conn.execute("SELECT id FROM poses WHERE name = ?", (pose_name,))
                pose_result = pose_cursor.fetchone()
                if pose_result:
                    conn.execute("""
                        INSERT INTO flow_poses (flow_id, pose_id, sequence_order, pose_duration)
                        VALUES (?, ?, ?, ?)
                    """, (flow_id, pose_result["id"], order, pose_duration))
        
        logger.info(f"Created flow: {flow_data['name']}")
        return True
    except sqlite3.IntegrityError:
        logger.error(f"Flow already exists: {flow_data['name']}")
        return False
    except Exception as e:
        logger.error(f"Error creating flow: {e}")
        return False

def get_all_flows() -> List[Dict[str, Any]]:
    """Get all flows with complete normalized data."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        # Get flow metadata with aggregated relationships
        cursor = conn.execute("""
            SELECT f.*,
                   GROUP_CONCAT(DISTINCT ys.name) as style_names,
                   GROUP_CONCAT(DISTINCT mg.name) as muscle_group_names
            FROM flows f
            LEFT JOIN flow_styles fs ON f.id = fs.flow_id
            LEFT JOIN yoga_styles ys ON fs.style_id = ys.id
            LEFT JOIN flow_muscle_groups fmg ON f.id = fmg.flow_id
            LEFT JOIN muscle_groups mg ON fmg.muscle_group_id = mg.id
            GROUP BY f.id
            ORDER BY f.name
        """)
        
        flows = []
        for row in cursor.fetchall():
            flow_id = row["id"]
            
            # Get poses for this flow
            pose_cursor = conn.execute("""
                SELECT p.name, fp.pose_duration, fp.sequence_order, p.type
                FROM flow_poses fp
                JOIN poses p ON fp.pose_id = p.id
                WHERE fp.flow_id = ?
                ORDER BY fp.sequence_order
            """, (flow_id,))
            
            flow_poses = []
            for pose_row in pose_cursor.fetchall():
                flow_poses.append({
                    "name": pose_row["name"],
                    "duration": pose_row["pose_duration"],
                    "type": pose_row["type"]
                })
            
            styles = row["style_names"].split(",") if row["style_names"] else []
            muscle_groups = row["muscle_group_names"].split(",") if row["muscle_group_names"] else []
            
            flows.append({
                "id": row["id"],
                "name": row["name"],
                "duration": row["duration"],
                "category": row["category"] or "",
                "style": styles,
                "muscle_groups": muscle_groups,
                "difficulty": row["difficulty"],
                "energy_level": row["energy_level"] or "",
                "flow": flow_poses
            })
        
        return flows

def update_flow(original_name: str, flow_data: Dict[str, Any]) -> bool:
    """Update flow with normalized relationships."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            # Get flow ID
            cursor = conn.execute("SELECT id FROM flows WHERE name = ?", (original_name,))
            result = cursor.fetchone()
            if not result:
                logger.warning(f"No flow found with name: {original_name}")
                return False
            
            flow_id = result["id"]
            
            # Update flow metadata
            conn.execute("""
                UPDATE flows SET 
                    name = ?, duration = ?, category = ?, difficulty = ?,
                    energy_level = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                flow_data["name"], flow_data.get("duration", 0),
                flow_data.get("category", ""), flow_data.get("difficulty", 1),
                flow_data.get("energy_level", ""), flow_id
            ))
            
            # Update styles - delete old, insert new
            conn.execute("DELETE FROM flow_styles WHERE flow_id = ?", (flow_id,))
            for style_name in flow_data.get("style", []):
                style_id = ensure_yoga_style_exists(style_name)
                conn.execute(
                    "INSERT INTO flow_styles (flow_id, style_id) VALUES (?, ?)",
                    (flow_id, style_id)
                )
            
            # Update muscle groups - delete old, insert new
            conn.execute("DELETE FROM flow_muscle_groups WHERE flow_id = ?", (flow_id,))
            for muscle_name in flow_data.get("muscle_groups", []):
                muscle_id = ensure_muscle_group_exists(muscle_name)
                conn.execute(
                    "INSERT INTO flow_muscle_groups (flow_id, muscle_group_id) VALUES (?, ?)",
                    (flow_id, muscle_id)
                )
            
            # Update pose sequence - delete old, insert new
            conn.execute("DELETE FROM flow_poses WHERE flow_id = ?", (flow_id,))
            for order, pose_info in enumerate(flow_data.get("flow", [])):
                pose_name = pose_info.get("name", "")
                pose_duration = pose_info.get("duration")
                
                # Get pose ID by name
                pose_cursor = conn.execute("SELECT id FROM poses WHERE name = ?", (pose_name,))
                pose_result = pose_cursor.fetchone()
                if pose_result:
                    conn.execute("""
                        INSERT INTO flow_poses (flow_id, pose_id, sequence_order, pose_duration)
                        VALUES (?, ?, ?, ?)
                    """, (flow_id, pose_result["id"], order, pose_duration))
        
        logger.info(f"Updated flow: {original_name} -> {flow_data['name']}")
        return True
    except Exception as e:
        logger.error(f"Error updating flow: {e}")
        return False

def delete_flow(flow_name: str) -> bool:
    """Delete a flow and all its relationships."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM flows WHERE name = ?", (flow_name,))
            
            if cursor.rowcount == 0:
                logger.warning(f"No flow found with name: {flow_name}")
                return False
        
        logger.info(f"Deleted flow: {flow_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting flow: {e}")
        return False

# SEQUENCE OPERATIONS
def create_sequence(sequence_data: Dict[str, Any]) -> bool:
    """Create sequence with normalized relationships."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            # Insert sequence metadata
            cursor = conn.execute("""
                INSERT INTO sequences (name, total_duration, difficulty)
                VALUES (?, ?, ?)
            """, (
                sequence_data["name"], sequence_data.get("total_duration", 0),
                sequence_data.get("difficulty", 1)
            ))
            
            sequence_id = cursor.lastrowid
            
            # Link styles
            for style_name in sequence_data.get("style", []):
                style_id = ensure_yoga_style_exists(style_name)
                conn.execute(
                    "INSERT INTO sequence_styles (sequence_id, style_id) VALUES (?, ?)",
                    (sequence_id, style_id)
                )
            
            # Link muscle groups
            for muscle_name in sequence_data.get("muscle_groups", []):
                muscle_id = ensure_muscle_group_exists(muscle_name)
                conn.execute(
                    "INSERT INTO sequence_muscle_groups (sequence_id, muscle_group_id) VALUES (?, ?)",
                    (sequence_id, muscle_id)
                )
            
            # Link flows in sections
            for section_type, flows_list in sequence_data.get("flows", {}).items():
                for order, flow_info in enumerate(flows_list):
                    flow_name = flow_info.get("name", "")
                    
                    # Get flow ID by name
                    flow_cursor = conn.execute("SELECT id FROM flows WHERE name = ?", (flow_name,))
                    flow_result = flow_cursor.fetchone()
                    if flow_result:
                        conn.execute("""
                            INSERT INTO sequence_flows (sequence_id, flow_id, section_type, sequence_order)
                            VALUES (?, ?, ?, ?)
                        """, (sequence_id, flow_result["id"], section_type, order))
        
        logger.info(f"Created sequence: {sequence_data['name']}")
        return True
    except sqlite3.IntegrityError:
        logger.error(f"Sequence already exists: {sequence_data['name']}")
        return False
    except Exception as e:
        logger.error(f"Error creating sequence: {e}")
        return False

def get_all_sequences() -> List[Dict[str, Any]]:
    """Get all sequences with complete normalized data."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT s.*,
                   GROUP_CONCAT(DISTINCT ys.name) as style_names,
                   GROUP_CONCAT(DISTINCT mg.name) as muscle_group_names
            FROM sequences s
            LEFT JOIN sequence_styles ss ON s.id = ss.sequence_id
            LEFT JOIN yoga_styles ys ON ss.style_id = ys.id
            LEFT JOIN sequence_muscle_groups smg ON s.id = smg.sequence_id
            LEFT JOIN muscle_groups mg ON smg.muscle_group_id = mg.id
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """)
        
        sequences = []
        for row in cursor.fetchall():
            sequence_id = row["id"]
            
            # Get flows organized by section
            flow_cursor = conn.execute("""
                SELECT f.name, f.duration, sf.section_type, sf.sequence_order
                FROM sequence_flows sf
                JOIN flows f ON sf.flow_id = f.id
                WHERE sf.sequence_id = ?
                ORDER BY sf.section_type, sf.sequence_order
            """, (sequence_id,))
            
            flows_by_section = {}
            for flow_row in flow_cursor.fetchall():
                section = flow_row["section_type"]
                if section not in flows_by_section:
                    flows_by_section[section] = []
                
                flows_by_section[section].append({
                    "name": flow_row["name"],
                    "duration": flow_row["duration"]
                })
            
            styles = row["style_names"].split(",") if row["style_names"] else []
            muscle_groups = row["muscle_group_names"].split(",") if row["muscle_group_names"] else []
            
            sequences.append({
                "id": row["id"],
                "name": row["name"],
                "total_duration": row["total_duration"],
                "difficulty": row["difficulty"],
                "style": styles,
                "muscle_groups": muscle_groups,
                "flows": flows_by_section,
                "created_at": row["created_at"]
            })
        
        return sequences

# FAVORITES OPERATIONS
def create_favorite(name: str, item_type: str, item_id: int) -> bool:
    """Create a favorite reference to a pose, flow, or sequence."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            # Create favorite entry
            cursor = conn.execute("""
                INSERT INTO favorites (name, type) VALUES (?, ?)
            """, (name, item_type))
            
            favorite_id = cursor.lastrowid
            
            # Link to appropriate item
            if item_type == "pose":
                conn.execute(
                    "INSERT INTO favorite_poses (favorite_id, pose_id) VALUES (?, ?)",
                    (favorite_id, item_id)
                )
            elif item_type == "flow":
                conn.execute(
                    "INSERT INTO favorite_flows (favorite_id, flow_id) VALUES (?, ?)",
                    (favorite_id, item_id)
                )
            elif item_type == "sequence":
                conn.execute(
                    "INSERT INTO favorite_sequences (favorite_id, sequence_id) VALUES (?, ?)",
                    (favorite_id, item_id)
                )
        
        logger.info(f"Created favorite: {name} ({item_type})")
        return True
    except Exception as e:
        logger.error(f"Error creating favorite: {e}")
        return False

def get_all_favorites() -> List[Dict[str, Any]]:
    """Get all favorites with complete data."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM favorites ORDER BY created_at DESC")
        favorites = []
        
        for row in cursor.fetchall():
            favorite = {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "created_at": row["created_at"]
            }
            
            # Get the actual favorited item data
            if row["type"] == "pose":
                pose_cursor = conn.execute("""
                    SELECT p.* FROM favorite_poses fp
                    JOIN poses p ON fp.pose_id = p.id
                    WHERE fp.favorite_id = ?
                """, (row["id"],))
                pose_data = pose_cursor.fetchone()
                if pose_data:
                    favorite["pose_data"] = dict(pose_data)
            
            elif row["type"] == "flow":
                flow_cursor = conn.execute("""
                    SELECT f.* FROM favorite_flows ff
                    JOIN flows f ON ff.flow_id = f.id
                    WHERE ff.favorite_id = ?
                """, (row["id"],))
                flow_data = flow_cursor.fetchone()
                if flow_data:
                    favorite["flow_data"] = dict(flow_data)
            
            elif row["type"] == "sequence":
                seq_cursor = conn.execute("""
                    SELECT s.* FROM favorite_sequences fs
                    JOIN sequences s ON fs.sequence_id = s.id
                    WHERE fs.favorite_id = ?
                """, (row["id"],))
                sequence_data = seq_cursor.fetchone()
                if sequence_data:
                    favorite["sequence_data"] = dict(sequence_data)
            
            favorites.append(favorite)
        
        return favorites

def delete_favorite(favorite_id: int) -> bool:
    """Delete a favorite by ID."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM favorites WHERE id = ?", (favorite_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"No favorite found with ID: {favorite_id}")
                return False
        
        logger.info(f"Deleted favorite ID: {favorite_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting favorite: {e}")
        return False

def get_favorite_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get favorite by name for updating."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM favorites WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result:
            return {
                "id": result["id"],
                "name": result["name"],
                "type": result["type"],
                "created_at": result["created_at"]
            }
        return None

# PRACTICE SESSION OPERATIONS
def create_practice_session(session_data: Dict[str, Any]) -> bool:
    """Create a practice session record."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            conn.execute("""
                INSERT INTO practice_sessions (sequence_id, duration_minutes, rating, notes)
                VALUES (?, ?, ?, ?)
            """, (
                session_data.get("sequence_id"),
                session_data.get("duration_minutes", 0),
                session_data.get("rating", 3),
                session_data.get("notes", "")
            ))
        
        logger.info(f"Created practice session")
        return True
    except Exception as e:
        logger.error(f"Error creating practice session: {e}")
        return False

def get_practice_sessions(sequence_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get practice sessions, optionally filtered by sequence."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        if sequence_id:
            cursor = conn.execute("""
                SELECT ps.*, s.name as sequence_name
                FROM practice_sessions ps
                LEFT JOIN sequences s ON ps.sequence_id = s.id
                WHERE ps.sequence_id = ?
                ORDER BY ps.session_date DESC
            """, (sequence_id,))
        else:
            cursor = conn.execute("""
                SELECT ps.*, s.name as sequence_name
                FROM practice_sessions ps
                LEFT JOIN sequences s ON ps.sequence_id = s.id
                ORDER BY ps.session_date DESC
            """)
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row["id"],
                "sequence_id": row["sequence_id"],
                "sequence_name": row["sequence_name"],
                "session_date": row["session_date"],
                "duration_minutes": row["duration_minutes"],
                "rating": row["rating"],
                "notes": row["notes"] or ""
            })
        
        return sessions

# UTILITY FUNCTIONS
def get_all_muscle_groups() -> List[str]:
    """Get all muscle group names."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT name FROM muscle_groups ORDER BY name")
        return [row["name"] for row in cursor.fetchall()]

def get_all_yoga_styles() -> List[str]:
    """Get all yoga style names."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT name FROM yoga_styles ORDER BY name")
        return [row["name"] for row in cursor.fetchall()]

def get_flow_with_full_poses(flow_id: int) -> Optional[Dict[str, Any]]:
    """Get flow with complete pose information for editing."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        # Get flow metadata
        cursor = conn.execute("SELECT * FROM flows WHERE id = ?", (flow_id,))
        flow_row = cursor.fetchone()
        if not flow_row:
            return None
        
        # Get poses with full details
        pose_cursor = conn.execute("""
            SELECT p.*, fp.pose_duration, fp.sequence_order
            FROM flow_poses fp
            JOIN poses p ON fp.pose_id = p.id
            WHERE fp.flow_id = ?
            ORDER BY fp.sequence_order
        """, (flow_id,))
        
        flow_poses = []
        for pose_row in pose_cursor.fetchall():
            # Get muscle groups for this pose
            muscle_cursor = conn.execute("""
                SELECT mg.name FROM pose_muscle_groups pmg
                JOIN muscle_groups mg ON pmg.muscle_group_id = mg.id
                WHERE pmg.pose_id = ?
            """, (pose_row["id"],))
            
            muscle_groups = [row["name"] for row in muscle_cursor.fetchall()]
            
            flow_poses.append({
                "id": pose_row["id"],
                "name": pose_row["name"],
                "duration": pose_row["pose_duration"],
                "type": pose_row["type"],
                "muscle_groups": muscle_groups,
                "difficulty": pose_row["difficulty"],
                "description": pose_row["description"],
                "instructions": pose_row["instructions"],
                "modifications": pose_row["modifications"],
                "image_filename": pose_row["image_filename"]
            })
        
        # Get styles and muscle groups for flow
        style_cursor = conn.execute("""
            SELECT ys.name FROM flow_styles fs
            JOIN yoga_styles ys ON fs.style_id = ys.id
            WHERE fs.flow_id = ?
        """, (flow_id,))
        styles = [row["name"] for row in style_cursor.fetchall()]
        
        muscle_cursor = conn.execute("""
            SELECT mg.name FROM flow_muscle_groups fmg
            JOIN muscle_groups mg ON fmg.muscle_group_id = mg.id
            WHERE fmg.flow_id = ?
        """, (flow_id,))
        muscle_groups = [row["name"] for row in muscle_cursor.fetchall()]
        
        return {
            "id": flow_row["id"],
            "name": flow_row["name"],
            "duration": flow_row["duration"],
            "category": flow_row["category"],
            "difficulty": flow_row["difficulty"],
            "energy_level": flow_row["energy_level"],
            "style": styles,
            "muscle_groups": muscle_groups,
            "flow": flow_poses,
            "created_at": flow_row["created_at"]
        }

# MIGRATION UTILITY
def migrate_from_json_data(json_poses_file: str, json_flows_file: str) -> bool:
    """Migrate existing JSON data to normalized database."""
    try:
        with open(json_poses_file) as f:
            poses_data = json.load(f)
        
        with open(json_flows_file) as f:
            flows_data = json.load(f)
        
        # Migrate poses
        for pose_info in poses_data.get("poses", {}).values():
            create_pose(pose_info)
        
        # Migrate flows
        for flow_info in flows_data.get("flowing_sequences", {}).values():
            create_flow(flow_info)
        
        logger.info("JSON data migration completed")
        return True
        
    except Exception as e:
        logger.error(f"Error migrating JSON data: {e}")
        return False