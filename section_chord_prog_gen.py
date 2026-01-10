from chord_generation_model import ProgressionSummary
import random

SECTION_CONFIG = {
  "intro": {
    "motion_max": 0.50,
    "dominant_max": 1,
    "ending_dominant": False,
    "bias_delta": {
      "suspenseful_tense": -0.2,
      "dark_brooding": -0.1,
      "calm_meditative": 0.1
    }
  },
  "verse": {
    "motion_min": 0.50,
    "motion_max": 0.75,
    "dominant_max": 2,
  },
  "chorus": {
    "motion_min": 0.50,
    "dominant_min": 1,
    "ending_tonic": True,
    "bias_delta": {
      "motivational_triumphant": 0.2,
      "happy_uplifting": 0.2
    }
  }
}





def check_if_motion_in_range(section_attributes:dict, motion_penalty:float)->bool:
    
    min_motion = section_attributes.get('motion_min', 0.0)
    max_motion = section_attributes.get('motion_max', 1.0)

    return motion_penalty >= min_motion and motion_penalty <= max_motion

def check_if_dominant_valid(section_attributes:dict , function_seq:list[str])->bool:
    max_dominant = section_attributes.get('dominant_max', len(function_seq))
    min_dominant = section_attributes.get('dominant_min', 0)

    dominant_count = 0

    for seq in function_seq:
        if seq == 'D':
            dominant_count+=1

    does_end_with_dom = function_seq[-1] == 'D'

    if "ending_dominant" in section_attributes:
        if section_attributes["ending_dominant"] != does_end_with_dom:
            return False

    return dominant_count <= max_dominant and dominant_count >= min_dominant


def check_if_tonic_valid(section_attributes:dict , last_function:str)->bool:
    
    does_end_with_tonic = last_function == 'T'

    if section_attributes.get('ending_tonic') and section_attributes['ending_tonic'] != does_end_with_tonic:
        return False
    
    return True


def get_effective_weights(emotion_bias:dict[str, float] , progression_pattern_summary: list[ProgressionSummary], section_attributes:dict , exclude:list[str]):
    result:list[float] = []
    positive_weighted_pattern:list[ProgressionSummary] = []

    for pattern in progression_pattern_summary:
        pattern_emotion_score = pattern['emotion_scores']
        emotion_score:float = 0.0
        
        for k in pattern_emotion_score.keys():
            if emotion_bias.get(k):
                emotion_score += (emotion_bias.get(k) * pattern_emotion_score.get(k))
        
        motion_penalty: float = len(set(pattern['roman_sequence'])) / len(pattern['roman_sequence'])

        effective_weight:float = emotion_score * pattern['base_weight'] * motion_penalty

            
        is_motion_in_range = check_if_motion_in_range(section_attributes, motion_penalty)

        is_dominant_valid = check_if_dominant_valid(section_attributes, pattern["function_sequence"])

        is_tonic_valid = check_if_tonic_valid(section_attributes, pattern["function_sequence"][-1])


        if effective_weight > 0 and is_motion_in_range and is_dominant_valid and is_tonic_valid and pattern["roman_sequence"] != exclude:
            positive_weighted_pattern.append(pattern)
            result.append(effective_weight)


    return result , positive_weighted_pattern




def get_chord_prog(section_attributes:dict , prompt_emotion_bias:dict , progression_pattern_summary : list[ProgressionSummary], exclude:list[str])->list[str]:
   
    bias_delta:dict = section_attributes.get('bias_delta')

    emotion_bias = prompt_emotion_bias.copy()

    if bias_delta and len(bias_delta)>0:
        for emotion in bias_delta.keys():
            if emotion_bias.get(emotion):
                emotion_bias[emotion] = min(max(emotion_bias[emotion] + bias_delta[emotion] , 0.0 ), 1.0) # normalized updated bias

    weights:list[float] = []
    progression_patterns:list[ProgressionSummary] = [] 

    weights, progression_patterns = get_effective_weights(emotion_bias , progression_pattern_summary, section_attributes , exclude)

    chosen_progression_summary:ProgressionSummary = random.choices(progression_patterns, weights, k=1)[0]

    return chosen_progression_summary["roman_sequence"]




def get_all_section_progression(prompt_emotion_bias, progression_pattern_summary)->list[str]:
    sections_chord_prog:list[str] = []
    previous_chord_prog:list[str] = []
    for _, section_attributes in SECTION_CONFIG.items():
        chord_prog =  get_chord_prog(section_attributes,prompt_emotion_bias, progression_pattern_summary, previous_chord_prog)
        previous_chord_prog = chord_prog
        sections_chord_prog.extend(chord_prog)


    print(sections_chord_prog)

    return sections_chord_prog



