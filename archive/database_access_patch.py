# database_access_patch.py
"""
Patch file to fix database access methods after migration.
Add these methods to your database_utils.py or create a separate patch file.
"""

import json
from utils.database_utils import get_db_manager

def get_all_sequences_fixed():
    """Get all sequences with proper normalized data structure."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT s.*, GROUP_CONCAT(DISTINCT ys.name) as style_names
            FROM sequences s
            LEFT JOIN sequence_styles ss ON s.id = ss.sequence_id
            LEFT JOIN yoga_styles ys ON ss.style_id = ys.id
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """)
        
        sequences = []
        for row in cursor.fetchall():
            # Parse the stored sequence data
            sequence_data = {}
            if row["sequence_data"]:
                try:
                    sequence_data = json.loads(row["sequence_data"])
                except json.JSONDecodeError:
                    sequence_data = {}
            
            # Build the sequence object
            styles = []
            if row["style_names"]:
                styles = row["style_names"].split(",")
            elif row["style"]:  # Fallback to JSON field
                try:
                    styles = json.loads(row["style"])
                except:
                    styles = []
            
            sequences.append({
                "id": row["id"],
                "name": row["name"],
                "total_duration": row["total_duration"],
                "style": styles,
                "flows": sequence_data.get("flow", {}),  # This might need adjustment
                "created_at": row["created_at"]
            })
        
        return sequences

def get_all_favorites_fixed():
    """Get favorites with proper structure for widgets."""
    db = get_db_manager()
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT * FROM favorites ORDER BY created_at DESC")
        favorites = []
        
        for row in cursor.fetchall():
            favorite_data = {}
            if row["favorite_data"]:
                try:
                    favorite_data = json.loads(row["favorite_data"])
                except json.JSONDecodeError:
                    favorite_data = {}
            
            # Create a structure that your widgets expect
            favorite = {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "created_at": row["created_at"],
                # Add fields that widgets might expect
                "style": favorite_data.get("style", "unknown"),
                "duration": favorite_data.get("duration", "0 minutes"),
                "sequences": {}  # This might need to be populated differently
            }
            
            # If it's a sequence favorite, try to get the actual sequence data
            if row["type"] == "sequence":
                seq_cursor = conn.execute("""
                    SELECT fs.sequence_id, s.* FROM favorite_sequences fs
                    JOIN sequences s ON fs.sequence_id = s.id
                    WHERE fs.favorite_id = ?
                """, (row["id"],))
                
                seq_result = seq_cursor.fetchone()
                if seq_result:
                    # Add sequence data
                    if seq_result["sequence_data"]:
                        try:
                            seq_data = json.loads(seq_result["sequence_data"])
                            favorite["sequences"] = {
                                "warm_up": [seq_data],  # Simplified structure
                            }
                        except json.JSONDecodeError:
                            pass
            
            favorites.append(favorite)
        
        return favorites

# Monkey patch the functions temporarily
if __name__ == "__main__":
    # You can import and use these functions directly
    pass