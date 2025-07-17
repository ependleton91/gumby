# ui/build_sequence.py
import json
import pathlib

def generate_yoga_class(style, muscles, duration):
    """
    Main function that takes user preferences and returns a complete yoga class
    """
    # Your logic will go here
    pass

def load_sequences():
    file_path = pathlib.Path("app_data/sequences.json")
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def filter_sequences(sequences, user_style, user_muscles):

    flowing_sequences = sequences['flowing_sequences']
    matching_sequences = []
    
    for sequence_id, sequence_data in flowing_sequences.items():
        # Check if this sequence matches user's style
        sequences_style = sequence_data['style']
        style_matches = user_style.lower() in [s.lower() for s in sequences_style]

        # If it matches, add to matching_sequences
        if style_matches:
            matching_sequences.append(sequence_data)

    return matching_sequences

def build_class(sequences, user_style, filtered_sequences, target_duration):
    class_templates = sequences['class_structure_templates']
    class_sequences = []
    
    # Direct lookup - no mapping needed!
    template_name = user_style.lower()
    class_template = class_templates[template_name]
    
    structure = class_template['structure']
    ratios = class_template['ratios']
    
    # Calculate time for each section
    time_slots = []
    for ratio in ratios:
        slot_duration = target_duration * ratio
        time_slots.append(slot_duration)

    category_to_section = {
        'warm_up': 'warm_up',
        'cool_down': 'cool_down',
        'standing_flow': 'main_flow',
        'seated_flow': 'main_flow',
        'hip_opener': 'main_flow',
        'backbend_flow': 'main_flow'
    }
    
    energy_to_sections = {
        'calming': ['cool_down', 'warm_up'],
        'deeply_relaxing': ['cool_down'],
        'energizing': ['main_flow'],
        'peak': ['main_flow'],
        'releasing': ['main_flow'],
        'building': ['main_flow', 'warm_up']
        }
    
    #Next: fill each slot with appropriate sequences
    for i, (section_type, time_needed) in enumerate(zip(structure, time_slots)):
        print(f"Section {i+1}: Need a {section_type} sequence that's ~{time_needed} minutes")
        for sequence in filtered_sequences:
            if category_to_section.get(sequence['category']) == section_type:
                if sequence not in class_sequences:
                    class_sequences.append(sequence)
                    break 

    return class_sequences

# Test the full pipeline
if __name__ == "__main__":
    # Load sequences
    sequences = load_sequences()
    print("✅ Loaded sequences successfully")
    
    # Test filtering
    filtered = filter_sequences(sequences, "VINYASA", ["arms"])
    print(f"✅ Found {len(filtered)} Vinyasa sequences")
    
    # Test class building
    class_sequences = build_class(sequences, "VINYASA", filtered, 60)
    print(f"✅ Built class with {len(class_sequences)} sequences")
    
    # Print the results
    print("\n--- Generated Class ---")
    total_time = 0
    for i, seq in enumerate(class_sequences):
        print(f"{i+1}. {seq['name']} ({seq['duration']} min)")
        total_time += seq['duration']
    print(f"\nTotal class time: {total_time} minutes")