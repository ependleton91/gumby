#!/usr/bin/env python3
"""
Complete migration script for all JSON files:
- all_poses.json
- flows.json  
- class_templates.json
- user_favorites.json

Usage:
    python migrate_all_json_files.py --test-mode
    python migrate_all_json_files.py --backup-first
"""

import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from utils.database_utils import get_db_manager, create_favorite, create_pose, create_flow

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_class_template(template_name, template_data):
    """Create a class template configuration in the database."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            # Create class_templates table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS class_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    style_name TEXT UNIQUE NOT NULL,
                    warm_up_percentage REAL,
                    main_flow_percentage REAL,
                    cool_down_percentage REAL,
                    energy_progression TEXT,
                    max_difficulty_jump INTEGER,
                    requires_counter_poses BOOLEAN,
                    flow_style TEXT,
                    typical_peak_difficulty INTEGER,
                    min_flows INTEGER,
                    max_flows INTEGER,
                    time_tolerance REAL,
                    template_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert the template
            conn.execute("""
                INSERT INTO class_templates (
                    style_name, warm_up_percentage, main_flow_percentage, 
                    cool_down_percentage, energy_progression, max_difficulty_jump,
                    requires_counter_poses, flow_style, typical_peak_difficulty,
                    min_flows, max_flows, time_tolerance, template_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_name,
                template_data.get("warm_up_percentage", 0.25),
                template_data.get("main_flow_percentage", 0.5),
                template_data.get("cool_down_percentage", 0.25),
                template_data.get("energy_progression", ""),
                template_data.get("max_difficulty_jump", 1),
                template_data.get("requires_counter_poses", True),
                template_data.get("flow_style", ""),
                template_data.get("typical_peak_difficulty", 2),
                template_data.get("min_flows", 2),
                template_data.get("max_flows", 5),
                template_data.get("time_tolerance", 0.1),
                json.dumps(template_data)
            ))
        logger.info(f"Created class template: {template_name}")
        return True
    except Exception as e:
        logger.error(f"Error creating class template {template_name}: {e}")
        return False

def get_existing_names():
    """Get existing names from target database."""
    db = get_db_manager()
    
    try:
        with db.get_connection() as conn:
            # Get existing poses
            pose_cursor = conn.execute("SELECT name FROM poses")
            existing_poses = {row["name"] for row in pose_cursor.fetchall()}
            
            # Get existing flows
            flow_cursor = conn.execute("SELECT name FROM flows")
            existing_flows = {row["name"] for row in flow_cursor.fetchall()}
            
            # Get existing templates
            try:
                template_cursor = conn.execute("SELECT style_name FROM class_templates")
                existing_templates = {row["style_name"] for row in template_cursor.fetchall()}
            except:
                existing_templates = set()
            
            # Get existing sequences
            try:
                seq_cursor = conn.execute("SELECT name FROM sequences")
                existing_sequences = {row["name"] for row in seq_cursor.fetchall()}
            except:
                existing_sequences = set()
                
            # Get existing favorites
            try:
                fav_cursor = conn.execute("SELECT name, type FROM favorites")
                existing_favorites = {(row["name"], row["type"]) for row in fav_cursor.fetchall()}
            except:
                existing_favorites = set()
            
            return existing_poses, existing_flows, existing_templates, existing_sequences, existing_favorites
            
    except Exception as e:
        logger.error(f"Error getting existing names: {e}")
        return set(), set(), set(), set(), set()

def migrate_all_poses(test_mode=False, skip_existing=True):
    """Migrate poses from all_poses.json."""
    logger.info("Migrating poses from all_poses.json...")
    
    poses_file = Path("app_data/all_poses.json")
    if not poses_file.exists():
        logger.warning("No all_poses.json file found")
        return 0
    
    try:
        with open(poses_file, 'r', encoding='utf-8') as f:
            poses_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading all_poses.json: {e}")
        return 0
    
    poses = poses_data.get("poses", {})
    if not poses:
        return 0
    
    existing_poses, _, _, _, _ = get_existing_names() if skip_existing else (set(), set(), set(), set(), set())
    
    poses_to_migrate = {}
    poses_skipped = []
    
    for pose_key, pose_data in poses.items():
        pose_name = pose_data.get("name", "")
        if skip_existing and pose_name in existing_poses:
            poses_skipped.append(pose_name)
        else:
            poses_to_migrate[pose_key] = pose_data
    
    logger.info(f"Found {len(poses)} poses in all_poses.json")
    logger.info(f"Will migrate: {len(poses_to_migrate)}, skip: {len(poses_skipped)}")
    
    if test_mode:
        logger.info("TEST MODE: Would migrate these poses:")
        for pose_key, pose_data in list(poses_to_migrate.items())[:10]:
            logger.info(f"  - {pose_data.get('name', pose_key)} (difficulty {pose_data.get('difficulty', 'N/A')})")
        if len(poses_to_migrate) > 10:
            logger.info(f"  ... and {len(poses_to_migrate) - 10} more")
        return len(poses_to_migrate)
    
    # Actually migrate
    success_count = 0
    error_count = 0
    
    for pose_key, pose_data in poses_to_migrate.items():
        try:
            # Ensure required fields and handle data type conversions
            pose_data.setdefault("type", "main")
            pose_data.setdefault("description", "")
            pose_data.setdefault("instructions", "")
            pose_data.setdefault("modifications", "")
            pose_data.setdefault("image_filename", f"{pose_key}.png")
            
            # Convert string numbers to proper types
            if isinstance(pose_data.get("default_duration"), str):
                pose_data["default_duration"] = float(pose_data["default_duration"])
            if isinstance(pose_data.get("difficulty"), str):
                pose_data["difficulty"] = int(pose_data["difficulty"])
            
            # Ensure muscle_groups is a list
            muscle_groups = pose_data.get("muscle_groups", [])
            if isinstance(muscle_groups, str):
                muscle_groups = [m.strip() for m in muscle_groups.split(",") if m.strip()]
            pose_data["muscle_groups"] = muscle_groups
            
            if create_pose(pose_data):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Error migrating pose {pose_data.get('name', pose_key)}: {e}")
    
    logger.info(f"Poses: {success_count} migrated, {len(poses_skipped)} skipped, {error_count} errors")
    return success_count

def migrate_all_flows(test_mode=False, skip_existing=True):
    """Migrate flows from flows.json."""
    logger.info("Migrating flows from flows.json...")
    
    flows_file = Path("app_data/flows.json")
    if not flows_file.exists():
        logger.warning("No flows.json file found")
        return 0
    
    try:
        with open(flows_file, 'r', encoding='utf-8') as f:
            flows_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading flows.json: {e}")
        return 0
    
    flows = flows_data.get("flowing_sequences", {})
    if not flows:
        return 0
    
    _, existing_flows, _, _, _ = get_existing_names() if skip_existing else (set(), set(), set(), set(), set())
    
    flows_to_migrate = {}
    flows_skipped = []
    
    for flow_key, flow_data in flows.items():
        flow_name = flow_data.get("name", "")
        if skip_existing and flow_name in existing_flows:
            flows_skipped.append(flow_name)
        else:
            flows_to_migrate[flow_key] = flow_data
    
    logger.info(f"Found {len(flows)} flows in flows.json")
    logger.info(f"Will migrate: {len(flows_to_migrate)}, skip: {len(flows_skipped)}")
    
    if test_mode:
        logger.info("TEST MODE: Would migrate these flows:")
        for flow_key, flow_data in list(flows_to_migrate.items())[:10]:
            logger.info(f"  - {flow_data.get('name', flow_key)} ({flow_data.get('duration', 'N/A')} min)")
        if len(flows_to_migrate) > 10:
            logger.info(f"  ... and {len(flows_to_migrate) - 10} more")
        return len(flows_to_migrate)
    
    # Actually migrate
    success_count = 0
    error_count = 0
    
    for flow_key, flow_data in flows_to_migrate.items():
        try:
            # Set defaults
            flow_data.setdefault("duration", 0.0)
            flow_data.setdefault("category", "")
            flow_data.setdefault("style", [])
            flow_data.setdefault("muscle_groups", [])
            flow_data.setdefault("difficulty", 2)
            flow_data.setdefault("energy_level", "")
            flow_data.setdefault("tags", [])
            flow_data.setdefault("flow", [])
            
            # Ensure arrays are arrays
            for field in ["style", "muscle_groups", "tags"]:
                if isinstance(flow_data[field], str):
                    flow_data[field] = [flow_data[field]] if flow_data[field] else []
            
            # Calculate duration if needed
            if flow_data["duration"] == 0.0:
                poses = flow_data.get("flow", [])
                flow_data["duration"] = sum(pose.get("duration", 0) for pose in poses)
            
            if create_flow(flow_data):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Error migrating flow {flow_data.get('name', flow_key)}: {e}")
    
    logger.info(f"Flows: {success_count} migrated, {len(flows_skipped)} skipped, {error_count} errors")
    return success_count

def migrate_class_templates(test_mode=False, skip_existing=True):
    """Migrate class templates from class_templates.json."""
    logger.info("Migrating class templates from class_templates.json...")
    
    templates_file = Path("app_data/class_templates.json")
    if not templates_file.exists():
        logger.warning("No class_templates.json file found")
        return 0
    
    try:
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading class_templates.json: {e}")
        return 0
    
    class_templates = templates_data.get("class_structure_templates", {})
    if not class_templates:
        return 0
    
    _, _, existing_templates, _, _ = get_existing_names() if skip_existing else (set(), set(), set(), set(), set())
    
    templates_to_migrate = {}
    templates_skipped = []
    
    for style_name, template_data in class_templates.items():
        if skip_existing and style_name in existing_templates:
            templates_skipped.append(style_name)
        else:
            templates_to_migrate[style_name] = template_data
    
    logger.info(f"Found {len(class_templates)} class templates")
    logger.info(f"Will migrate: {len(templates_to_migrate)}, skip: {len(templates_skipped)}")
    
    if test_mode:
        logger.info("TEST MODE: Would migrate these class templates:")
        for style_name in templates_to_migrate.keys():
            logger.info(f"  - {style_name}")
        return len(templates_to_migrate)
    
    # Actually migrate
    success_count = 0
    error_count = 0
    
    for style_name, template_data in templates_to_migrate.items():
        try:
            if create_class_template(style_name, template_data):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Error migrating class template {style_name}: {e}")
    
    logger.info(f"Class templates: {success_count} migrated, {len(templates_skipped)} skipped, {error_count} errors")
    return success_count

def migrate_user_favorites(test_mode=False, skip_existing=True):
    """Migrate user favorites from user_favorites.json."""
    logger.info("Migrating user favorites from user_favorites.json...")
    
    favorites_file = Path("app_data/user_favorites.json")
    if not favorites_file.exists():
        logger.warning("No user_favorites.json file found")
        return 0
    
    try:
        with open(favorites_file, 'r', encoding='utf-8') as f:
            favorites_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading user_favorites.json: {e}")
        return 0
    
    favorites = favorites_data.get("favorites", [])
    if not favorites:
        return 0
    
    _, _, _, existing_sequences, existing_favorites = get_existing_names() if skip_existing else (set(), set(), set(), set(), set())
    
    # Process favorites and sequences
    favorites_to_migrate = []
    sequences_to_create = []
    
    for fav_data in favorites:
        fav_name = fav_data.get("name", "Unknown")
        fav_type = "sequence"
        
        # Check favorite
        if not skip_existing or (fav_name, fav_type) not in existing_favorites:
            favorites_to_migrate.append(fav_data)
        
        # Check sequences within favorite
        sequences = fav_data.get("sequences", {})
        for section_name, flows in sequences.items():
            for flow in flows:
                sequence_name = f"{fav_name} - {flow['name']}"
                if not skip_existing or sequence_name not in existing_sequences:
                    sequences_to_create.append((fav_data, flow))
    
    total_items = len(favorites_to_migrate) + len(sequences_to_create)
    
    logger.info(f"Found {len(favorites)} favorites")
    logger.info(f"Will migrate: {len(favorites_to_migrate)} favorites, {len(sequences_to_create)} sequences")
    
    if test_mode:
        logger.info("TEST MODE: Would migrate these items:")
        for fav_data in favorites_to_migrate:
            logger.info(f"  - Favorite: {fav_data['name']}")
        for fav_data, flow in sequences_to_create[:5]:
            sequence_name = f"{fav_data['name']} - {flow['name']}"
            logger.info(f"  - Sequence: {sequence_name}")
        if len(sequences_to_create) > 5:
            logger.info(f"  ... and {len(sequences_to_create) - 5} more sequences")
        return total_items
    
    # Actually migrate
    success_count = 0
    error_count = 0
    
    # Migrate favorites
    for fav_data in favorites_to_migrate:
        try:
            favorite_record = {
                "name": fav_data["name"],
                "type": "sequence",
                "description": fav_data.get("description", ""),
                "duration": fav_data.get("duration", ""),
                "style": fav_data.get("style", ""),
                "muscles": fav_data.get("muscles", []),
                "created_date": fav_data.get("created_date", "")
            }
            
            if create_favorite(favorite_record):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Error migrating favorite {fav_data.get('name', 'Unknown')}: {e}")
    
    # Create sequences
    for fav_data, flow in sequences_to_create:
        try:
            sequence_name = f"{fav_data['name']} - {flow['name']}"
            
            total_duration = flow.get("duration", 0.0)
            if total_duration == 0.0:
                poses = flow.get("flow", [])
                total_duration = sum(pose.get("duration", 0) for pose in poses)
            
            db = get_db_manager()
            with db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO sequences (
                        name, total_duration, style, muscle_groups, sequence_data
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    sequence_name,
                    total_duration,
                    json.dumps(flow.get("style", [])),
                    json.dumps(flow.get("muscle_groups", [])),
                    json.dumps(flow)
                ))
            
            success_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Error creating sequence {sequence_name}: {e}")
    
    logger.info(f"Favorites/sequences: {success_count} migrated, {error_count} errors")
    return success_count

def check_what_would_migrate():
    """Show what would be migrated from all JSON files."""
    logger.info("🔍 Checking what would be migrated from all JSON files...\n")
    
    total = 0
    
    logger.info("📋 ALL_POSES.JSON:")
    poses_count = migrate_all_poses(test_mode=True, skip_existing=True)
    total += poses_count
    
    print()
    logger.info("🌊 FLOWS.JSON:")
    flows_count = migrate_all_flows(test_mode=True, skip_existing=True)
    total += flows_count
    
    print()
    logger.info("📐 CLASS_TEMPLATES.JSON:")
    templates_count = migrate_class_templates(test_mode=True, skip_existing=True)
    total += templates_count
    
    print()
    logger.info("⭐ USER_FAVORITES.JSON:")
    favorites_count = migrate_user_favorites(test_mode=True, skip_existing=True)
    total += favorites_count
    
    print(f"\n📊 SUMMARY: {total} total items would be migrated")
    return total

def main():
    parser = argparse.ArgumentParser(description="Migrate all JSON files to gumby database")
    parser.add_argument("--test-mode", action="store_true",
                       help="Show what would be migrated")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                       help="Skip items that already exist (default)")
    parser.add_argument("--force-all", action="store_true",
                       help="Try to insert all items")
    parser.add_argument("--backup-first", action="store_true",
                       help="Create backup before migration")
    parser.add_argument("--check-only", action="store_true",
                       help="Just show what would be migrated")
    
    args = parser.parse_args()
    
    if args.check_only:
        total = check_what_would_migrate()
        if total > 0:
            print(f"\n💡 To migrate these items, run:")
            print(f"   python {__file__} --backup-first")
        else:
            print(f"\n✅ Nothing to migrate - you're all set!")
        return
    
    # Determine skip mode
    skip_existing = not args.force_all
    if args.force_all:
        logger.warning("⚠️  Force mode: Will try to insert duplicates")
    else:
        logger.info("✅ Safe mode: Will skip existing items")
    
    logger.info("🚀 Starting complete JSON migration...")
    
    # Backup if requested  
    if args.backup_first and not args.test_mode:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(f"app_data/migration_backup_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        json_files = ["all_poses.json", "flows.json", "class_templates.json", "user_favorites.json"]
        for json_file in json_files:
            source = Path("app_data") / json_file
            if source.exists():
                import shutil
                shutil.copy2(source, backup_dir / json_file)
                logger.info(f"📁 Backed up: {json_file}")
        
        logger.info(f"📁 Backup created at: {backup_dir}")
    
    # Initialize target database
    if not args.test_mode:
        get_db_manager()  # Creates gumby.db and tables
        logger.info("📊 Database initialized")
    
    # Run all migrations
    total_migrated = 0
    
    try:
        # Migrate poses
        poses_count = migrate_all_poses(args.test_mode, skip_existing)
        total_migrated += poses_count
        
        # Migrate flows
        flows_count = migrate_all_flows(args.test_mode, skip_existing)
        total_migrated += flows_count
        
        # Migrate class templates
        templates_count = migrate_class_templates(args.test_mode, skip_existing)
        total_migrated += templates_count
        
        # Migrate favorites
        favorites_count = migrate_user_favorites(args.test_mode, skip_existing)
        total_migrated += favorites_count
        
        if args.test_mode:
            logger.info(f"🧪 TEST MODE: Would migrate {total_migrated} total items")
        else:
            logger.info(f"✅ Migration complete! Migrated {total_migrated} total items")
            if total_migrated > 0:
                logger.info("🎉 All your JSON data is now in gumby.db!")
            else:
                logger.info("ℹ️  Everything was already in the database")
    
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    
    logger.info("🏁 Complete JSON migration finished")

if __name__ == "__main__":
    main()