# services/sequence_builder.py
from dataclasses import dataclass
from typing import List, Dict, Any
from utils.file_utils import load_flows_data
from utils.sequence_utils import (
    extract_unique_values, filter_flows_by_criteria, 
    select_flows_for_sequence, load_class_template,
    group_flows_by_category, calculate_total_sequence_duration,
    get_sequence_muscle_groups
)
from utils.display_utils import format_for_internal, format_list_for_internal, format_list_for_display
from config import CLASS_TEMPLATES_FILE

@dataclass
class SequenceRequest:
    style: str
    target_muscles: List[str]
    duration: int

@dataclass
class SequenceResult:
    sequences: Dict[str, List[Dict]]
    total_duration: float
    muscles_covered: List[str]

class SequenceBuilder:
    def __init__(self):
        self.flows_data = load_flows_data()
        self.available_styles = self._extract_available_styles()
        self.available_muscles = self._extract_available_muscles()
    
    def _extract_available_styles(self) -> List[str]:
        """Pull all unique styles from flows data - exact wording"""
        return extract_unique_values(self.flows_data, "style")
    
    def _extract_available_muscles(self) -> List[str]:
        """Pull all unique muscle groups from flows data - exact wording"""  
        return extract_unique_values(self.flows_data, "muscle_groups")
    
    def generate_sequence(self, request: SequenceRequest) -> SequenceResult:
        # Convert display format to internal format
        internal_style = format_for_internal(request.style)
        internal_muscles = format_list_for_internal(request.target_muscles)
        
        # Use the advanced sequence_utils
        user_preferences = {
            "duration": request.duration,
            "style": internal_style,
            "muscle_groups": internal_muscles
        }
        
        selected_flows = select_flows_for_sequence(user_preferences)
        
        # Group flows into sections based on their categories
        flows_by_category = group_flows_by_category(selected_flows)
        
        # Organize into the structure expected by your existing UI
        organized_sequences = {
            "warm_up": flows_by_category.get("warm_up", []),
            "main_flow": [],
            "cool_down": flows_by_category.get("cool_down", [])
        }
        
        # Combine all main flow categories into "main_flow" section
        main_flow_categories = ["standing_flow", "seated_flow", "hip_opener", "backbend_flow"]
        for category in main_flow_categories:
            if category in flows_by_category:
                organized_sequences["main_flow"].extend(flows_by_category[category])
        
        # Calculate results - FIXED: Use only flow-level durations
        total_duration = self._calculate_fixed_duration(selected_flows)
        
        # Get muscle groups covered and convert back to display format
        muscles_covered_internal = get_sequence_muscle_groups(selected_flows)
        muscles_covered = format_list_for_display(muscles_covered_internal)
        
        return SequenceResult(
            sequences=organized_sequences,
            total_duration=total_duration,
            muscles_covered=muscles_covered
        )
    
    def _calculate_fixed_duration(self, flows: List[Dict[str, Any]]) -> float:
        """Fixed duration calculation - use ONLY flow-level durations."""
        total = 0.0
        print("=== DURATION CALCULATION DEBUG ===")
        
        for flow in flows:
            flow_duration = flow.get("duration", 0)
            total += flow_duration
            
            # Also check if there are individual pose durations
            flow_poses = flow.get("flow", [])
            pose_duration_sum = sum(pose.get("duration", 0) for pose in flow_poses)
            
            print(f"Flow: {flow.get('name', 'Unknown')}")
            print(f"  Flow-level duration: {flow_duration}min")
            print(f"  Sum of pose durations: {pose_duration_sum}min")
            print(f"  Difference: {abs(flow_duration - pose_duration_sum):.1f}min")
        
        print(f"Total calculated duration: {total} minutes")
        print("=== END DURATION DEBUG ===")
        
        return round(total, 1)