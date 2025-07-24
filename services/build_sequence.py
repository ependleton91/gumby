# ui/build_sequence.py
import json
import pathlib
import random

def generate_yoga_class(style, muscles, duration):
    #initialze variables
   class_duration = 0
   muscles_used = []
   print(f"Requested muscles: {muscles}")

   #map ui text to json text
   ui_to_json = {
    "Abs": "core",
    "Arms": "arms", 
    "Back": "back",
    "Pelvic Floor": "pelvic_floor",
    "All": "full_body"
    }
   
   #use map to find muscles in json files 
   translated_muscles = [ui_to_json[muscle] for muscle in muscles]

   #read sequences from json 
   loaded_sequences = load_sequences()

   #filter for only sequences aligned with selected style
   print(f"Filtering for sequences that match style: {style}")
   filtered_sequences = filter_sequences(loaded_sequences,style)

   #generate yoga class with filtered sequences and user selections
   print(f"Generating yoga classes using filtered sequences to meet duration {duration} minutes and targeting muscle(s): [ {", ".join(translated_muscles)}]")
   generated_class = build_class(loaded_sequences,style,filtered_sequences,duration,translated_muscles)

   #grab all sequences from individual sections
   all_sequences=[]
   for value in generated_class.values():
        all_sequences.extend(value)

    #build results dictionary
   for sequence in all_sequences:
       class_duration+=sequence['duration']
       for muscle in muscles:
           if ui_to_json[muscle] in sequence['muscle_groups'] and muscle not in muscles_used:
               muscles_used.append(muscle) 
   results_dictionary = {"sequences":generated_class,"muscles":muscles_used,"duration":class_duration}

   return results_dictionary

def load_sequences():
    file_path = pathlib.Path("app_data/sequences.json")
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def filter_sequences(sequences, user_style):

    flowing_sequences = sequences['flowing_sequences']
    matching_sequences = []
    
    for sequence_id, sequence_data in flowing_sequences.items():
        # Check if this sequence matches user's style
        sequences_style = sequence_data['style']
        style_matches = user_style.lower() in [s.lower() for s in sequences_style]

        # If it matches, add to matching_sequences
        if style_matches:
            matching_sequences.append(sequence_data)
    print(f"Matching sequences compiled.")
    return matching_sequences

def calculate_muscle_percentage(selected_sequences,target_muscles):
    print(f"Calculating muscle percentage for current sequences.")
    muscle_sequences=0
    for sequence_data in selected_sequences:
        if any(muscle in target_muscles for muscle in sequence_data['muscle_groups']):
            muscle_sequences+=1

    if len(selected_sequences) == 0:
        muscle_percentage = 0.0
    else:
        muscle_percentage = muscle_sequences/len(selected_sequences)
    
    print(f"Target muscles are covered in {muscle_percentage}% of current sequences.")
    return muscle_percentage

def sequence_matches_muscles(sequence,muscles):
    #Check for muscle in current sequence
    return any(muscle in muscles for muscle in sequence['muscle_groups'])

def score_sequence(sequence, time_needed, target_muscles, current_percentage,desired_percentage):
    #build sequence variables
    sequence_score = 0
    #Has percentage goal been reached for muscle grouos?
    percentage_gap = desired_percentage-current_percentage

    #Don't add sequence if it will go over time
    if sequence['duration'] <= time_needed:
        sequence_score+=30
    else:
        sequence_score-=900
    
    #Bonus if target muscles inclded AND percentage goal not reached
    if any(muscle in target_muscles for muscle in sequence['muscle_groups']):
        sequence_score+=(percentage_gap*100)
    elif percentage_gap>0:
        sequence_score-=10

    sequence_score+= random.randint(0,20)

    return sequence_score

def select_from_top_candidates(scored_sequences):
    #sort by second tuple which is score
    scored_sequences.sort(key=lambda x: x[1],reverse = True)
    keep_count = max(3, int(len(scored_sequences) * 0.7))
    top_candidates = scored_sequences[:keep_count]
    chosen_sequence = random.choice(top_candidates)
    print(f"Sequence chosen: {chosen_sequence[0]['name']}")
    return chosen_sequence[0]


def build_class(sequences, user_style, filtered_sequences, target_duration, target_muscles):
    class_templates = sequences['class_structure_templates']
    class_sequences = {}

    # Grab template from json
    template_name = user_style.lower()
    class_template = class_templates[template_name]
    
    #Grab structure and ratio from json
    structure = class_template['structure']
    ratios = class_template['ratios']

    #Initialize dictionary for each section
    for section in structure:
        class_sequences[section]=[]
    
    # Calculate time for each section
    time_slots = []
    for ratio in ratios:
        slot_duration = target_duration * ratio
        time_slots.append(slot_duration)
    
    #Create structure/duration list
    timed_structure = zip(structure,time_slots)

    #Map category to section
    category_to_section = {
        'warm_up': 'warm_up',
        'cool_down': 'cool_down',
        'standing_flow': 'main_flow',
        'seated_flow': 'main_flow',
        'hip_opener': 'main_flow',
        'backbend_flow': 'main_flow'
    }
    
    #map energy level to section
    energy_to_sections = {
        'calming': ['cool_down', 'warm_up'],
        'deeply_relaxing': ['cool_down'],
        'energizing': ['main_flow'],
        'peak': ['main_flow'],
        'releasing': ['main_flow'],
        'building': ['main_flow', 'warm_up']
        }

    #Next: fill each slot with appropriate sequences
    for section in timed_structure:
        section_duration = 0
        desired_percentage = 0.6
        used_names=[]
        compatible_energy_levels = []
        for item in energy_to_sections.items():
            if section[0] in item[1]:
                compatible_energy_levels.append(item[0])
        while section_duration < section[1] * 0.8:
            all_sequences=[]
            for value in class_sequences.values():
                all_sequences.extend(value)
            muscle_group_coverage = calculate_muscle_percentage(all_sequences,target_muscles)
            section_sequences = []
            for sequence in filtered_sequences:
                if category_to_section[sequence['category']] == section[0] and sequence['name'] not in used_names:
                    section_sequences.append(sequence)
            if len(section_sequences) == 0:
                for sequence in filtered_sequences:
                    if category_to_section[sequence['category']] == section[0]:
                        section_sequences.append(sequence)    
            if len(section_sequences) == 0:
                for sequence in filtered_sequences:
                    if sequence['energy_level'] in compatible_energy_levels and sequence['name'] not in used_names:
                        section_sequences.append(sequence)
            if len(section_sequences)==0:
                for sequence in filtered_sequences:
                    if sequence['name'] not in used_names:
                        section_sequences.append(sequence)

            if len(section_sequences) == 0:
                raise Exception("Zero sequences found, please retry with different parameters")

            sequence_tuples = []
            for sequence in section_sequences:
                sequence_tuples.append((sequence,score_sequence(sequence,section[1],target_muscles,muscle_group_coverage,desired_percentage)))
            sequence_to_add = select_from_top_candidates(sequence_tuples)
            section_duration+=sequence_to_add['duration']
            class_sequences[section[0]].append(sequence_to_add)
            used_names.append(sequence_to_add['name'])

    return class_sequences