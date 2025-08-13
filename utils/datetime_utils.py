import logging
from datetime import datetime, timedelta, time
from typing import Optional, Tuple, Union
import re

logger = logging.getLogger(__name__)


def get_current_timestamp() -> str:
    #Get current timestamp in standard format for GUMBY.
    
    #Returns:
    #    Timestamp string in YYYY-MM-DD HH:MM:SS format
        
    #Example:    timestamp = get_current_timestamp()
    # Returns:    "2024-03-15 14:30:45"
    
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date() -> str:
    #Get current date in YYYY-MM-DD format.
    
    #Returns:
        #Date string in YYYY-MM-DD format
        
    #Example:
        #date = get_current_date()
        # Returns: "2024-03-15"
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time() -> str:
    #Get current time in HH:MM:SS format.
    
    #Returns:
        #Time string in HH:MM:SS format
        
    #Example:
        #time_str = get_current_time()
        # Returns: "14:30:45"
    return datetime.now().strftime("%H:%M:%S")


def format_duration_minutes(minutes: float, detailed: bool = False) -> str:
    #Format duration from minutes to readable string.
    
    #Args:
        #minutes: Duration in minutes
        #detailed: Whether to include seconds in output
        
    #Returns:
        #Formatted duration string
        
    #Example:
        #format_duration_minutes(90.5)     # "1h 30m"
        #format_duration_minutes(5.25)     # "5m 15s"
        #format_duration_minutes(0.5)      # "30s"

    if minutes <= 0:
        return "0s"
    
    total_seconds = int(minutes * 60)
    hours = total_seconds // 3600
    remaining_minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    
    if hours > 0:
        parts.append(f"{hours}h")
    
    if remaining_minutes > 0:
        parts.append(f"{remaining_minutes}m")
    
    if seconds > 0 and (detailed or len(parts) == 0):
        parts.append(f"{seconds}s")
    
    return " ".join(parts) if parts else "0s"


def format_duration_seconds(seconds: int) -> str:
    #Format duration from seconds to readable string.
    
    #Args:
    #    seconds: Duration in seconds
        
    #Returns:
    #    Formatted duration string
        
    #Example:
    #    format_duration_seconds(3665)  # "1h 1m 5s"
    #    format_duration_seconds(125)   # "2m 5s"
    #    format_duration_seconds(45)    # "45s"

    if seconds <= 0:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    
    parts = []
    
    if hours > 0:
        parts.append(f"{hours}h")
    
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    if remaining_seconds > 0 or len(parts) == 0:
        parts.append(f"{remaining_seconds}s")
    
    return " ".join(parts)


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    #Parse timestamp string back to datetime object.
    
    #Args:
    #    timestamp_str: Timestamp string in various formats
        
    #Returns:
    #    datetime object or None if parsing failed
        
    #Example:
    #    dt = parse_timestamp("2024-03-15 14:30:45")
    #    if dt:
    #        print(f"Parsed: {dt}")
    
    if not timestamp_str:
        return None
    
    # Try different timestamp formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str.strip(), fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse timestamp: {timestamp_str}")
    return None


def format_practice_duration(start_time: datetime, end_time: datetime) -> str:
    #Format practice session duration between two datetime objects.
    
    #Args:
    #    start_time: Session start time
    #    end_time: Session end time
        
    #Returns:
    #    Formatted duration string
        
    #Example:
    #    start = datetime.now()
    #    end = start + timedelta(minutes=45, seconds=30)
    #    duration = format_practice_duration(start, end)
    #    Returns: "45m 30s"
    
    if end_time <= start_time:
        return "0s"
    
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    
    return format_duration_seconds(total_seconds)


def calculate_session_duration(start_timestamp: str, end_timestamp: str) -> str:
    #Calculate duration between two timestamp strings.
    
    #Args:
    #    start_timestamp: Start time as string
    #    end_timestamp: End time as string
        
    #Returns:
    #    Formatted duration string or "Unknown" if parsing fails
    start_dt = parse_timestamp(start_timestamp)
    end_dt = parse_timestamp(end_timestamp)
    
    if not start_dt or not end_dt:
        return "Unknown"
    
    return format_practice_duration(start_dt, end_dt)


def format_time_ago(timestamp_str: str) -> str:
    #Format timestamp as "time ago" string (e.g., "2 hours ago").
    
    #Args:
    #    timestamp_str: Timestamp string
        
    #Returns:
    #    Human-readable "time ago" string
        
    #Example:
    #    time_ago = format_time_ago("2024-03-15 12:30:00")
    #    Returns: "2 hours ago" (if current time is 14:30)
    
    dt = parse_timestamp(timestamp_str)
    if not dt:
        return "Unknown time"
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    
    if diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    
    minutes = (diff.seconds % 3600) // 60
    if minutes > 0:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    
    return "Just now"


def format_timer_display(total_seconds: int) -> str:
    #Format seconds for timer display (MM:SS or HH:MM:SS).
    
    #Args:
    #    total_seconds: Time in seconds
        
    #Returns:
    #    Formatted time string for display
        
    #Example:
    #    format_timer_display(125)   # "02:05"
    #    format_timer_display(3665)  # "1:01:05"
    
    if total_seconds < 0:
        total_seconds = 0
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def parse_duration_input(duration_str: str) -> Optional[float]:
    #Parse various duration input formats to minutes.
    
    #Args:
    #    duration_str: Duration string (e.g., "5m", "1h 30m", "90", "1.5h")
        
    #Returns:
    #    Duration in minutes or None if parsing failed
        
    #Example:
    #    parse_duration_input("1h 30m")  # 90.0
    #    parse_duration_input("45")      # 45.0  
    #    parse_duration_input("1.5h")    # 90.0

    if not duration_str or not duration_str.strip():
        return None
    
    duration_str = duration_str.strip().lower()
    
    # Try simple number first (assume minutes)
    try:
        return float(duration_str)
    except ValueError:
        pass
    
    # Parse complex formats like "1h 30m" or "45s"
    total_minutes = 0.0
    
    # Extract hours
    hour_match = re.search(r'(\d+(?:\.\d+)?)\s*h', duration_str)
    if hour_match:
        total_minutes += float(hour_match.group(1)) * 60
    
    # Extract minutes
    min_match = re.search(r'(\d+(?:\.\d+)?)\s*m', duration_str)
    if min_match:
        total_minutes += float(min_match.group(1))
    
    # Extract seconds
    sec_match = re.search(r'(\d+(?:\.\d+)?)\s*s', duration_str)
    if sec_match:
        total_minutes += float(sec_match.group(1)) / 60
    
    return total_minutes if total_minutes > 0 else None


def is_recent_timestamp(timestamp_str: str, hours_threshold: int = 24) -> bool:
    #Check if timestamp is within recent threshold.
    
    #Args:
    #    timestamp_str: Timestamp string
    #    hours_threshold: Hours to consider "recent"
        
    #Returns:
    #    True if timestamp is recent
    dt = parse_timestamp(timestamp_str)
    if not dt:
        return False
    
    now = datetime.now()
    diff = now - dt
    
    return diff.total_seconds() < (hours_threshold * 3600)


def get_practice_session_summary(sessions: List[Dict]) -> Dict[str, Any]:
    #Generate summary statistics for practice sessions.
    
    #Args:
    #    sessions: List of practice session dictionaries
        
    #Returns:
    #    Dictionary with summary statistics
    if not sessions:
        return {
            "total_sessions": 0,
            "total_time": "0m",
            "average_duration": "0m",
            "last_practice": "Never"
        }
    
    total_minutes = 0.0
    valid_sessions = []
    
    for session in sessions:
        if "duration" in session:
            # Try to parse duration
            duration_parsed = parse_duration_input(str(session["duration"]))
            if duration_parsed:
                total_minutes += duration_parsed
                valid_sessions.append(session)
    
    if not valid_sessions:
        return {
            "total_sessions": len(sessions),
            "total_time": "0m",
            "average_duration": "0m", 
            "last_practice": "Unknown"
        }
    
    average_minutes = total_minutes / len(valid_sessions)
    
    # Find most recent session
    most_recent = None
    for session in valid_sessions:
        if "date" in session:
            session_dt = parse_timestamp(session["date"])
            if session_dt and (most_recent is None or session_dt > most_recent):
                most_recent = session_dt
    
    last_practice = format_time_ago(most_recent.strftime("%Y-%m-%d %H:%M:%S")) if most_recent else "Unknown"
    
    return {
        "total_sessions": len(valid_sessions),
        "total_time": format_duration_minutes(total_minutes),
        "average_duration": format_duration_minutes(average_minutes),
        "last_practice": last_practice
    }


# Convenience functions for GUMBY-specific date/time operations
def get_practice_date_display(timestamp_str: str) -> str:
#    Format practice date for display in UI.
    dt = parse_timestamp(timestamp_str)
    if not dt:
        return "Unknown date"
    
    return dt.strftime("%B %d, %Y at %I:%M %p")


def get_sequence_age_display(created_timestamp: str) -> str:
   #Format sequence creation date for display.
    return f"Created {format_time_ago(created_timestamp)}"