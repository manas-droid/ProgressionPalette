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

def _emotion_axes(emotion_bias: dict[str, float]) -> dict[str, float]:
    suspenseful_tense = float(emotion_bias.get("suspenseful_tense", 0.0))
    calm_meditative = float(emotion_bias.get("calm_meditative", 0.0))
    wistful_longing = float(emotion_bias.get("wistful_longing", 0.0))
    motivational_triumphant = float(emotion_bias.get("motivational_triumphant", 0.0))
    nostalgic_sentimental = float(emotion_bias.get("nostalgic_sentimental", 0.0))
    dark_brooding = float(emotion_bias.get("dark_brooding", 0.0))
    happy_uplifting = float(emotion_bias.get("happy_uplifting", 0.0))

    tension = suspenseful_tense + dark_brooding
    warmth = calm_meditative + nostalgic_sentimental
    lift = happy_uplifting + motivational_triumphant

    return {
        "tension": tension,
        "warmth": warmth,
        "lift": lift,
        "calm": calm_meditative,
        "wistful": wistful_longing,
        "nostalgia": nostalgic_sentimental,
        "dark": dark_brooding,
        "suspense": suspenseful_tense,
    }


def _weighted_choice(options: list[tuple[str, float]]) -> str:
    labels = [label for label, _ in options]
    weights = [max(weight, 0.0) for _, weight in options]
    total = sum(weights)
    if total == 0:
        return labels[0]
    return random.choices(labels, weights=weights, k=1)[0]


def _apply_extension_to_roman(roman_seq: str, extension: str) -> str:
    if extension == "":
        return roman_seq
    return f"{roman_seq}{extension}"


def choose_extension(
    roman_seq: str,
    function: str,
    mode: str,
    emotion_bias: dict[str, float],
) -> str:
    axes = _emotion_axes(emotion_bias)
    tension = axes["tension"]
    calm = axes["calm"]
    lift = axes["lift"]
    warmth = axes["warmth"]
    wistful = axes["wistful"]
    nostalgia = axes["nostalgia"]

    if function == "D":
        extension = _weighted_choice(
            [
                ("7", 1.0 + 0.5 * tension - 0.4 * calm),
                ("9", 0.6 + 0.6 * lift + 0.2 * warmth - 0.3 * calm),
                ("7b9", 0.2 + 1.2 * tension - 0.5 * calm),
                ("7#9", 0.2 + 1.0 * tension - 0.5 * calm),
                ("7#9b13", 0.1 + 1.4 * tension - 0.6 * calm),
            ]
        )
        return _apply_extension_to_roman(roman_seq, extension)

    is_upper = roman_seq[:1].isupper()
    is_lower = roman_seq[:1].islower()

    options: list[tuple[str, float]] = [
        ("", 1.1 + 0.8 * calm - 0.3 * tension),
        ("6", 0.3 + 0.7 * lift + 0.4 * nostalgia - 0.2 * tension),
        ("9", 0.2 + 0.6 * calm + 0.4 * warmth + 0.4 * lift - 0.2 * tension),
    ]

    if is_lower:
        options.append(("7", 0.4 + 0.6 * wistful + 0.3 * tension + 0.2 * warmth))
    if is_upper:
        options.append(("maj7", 0.3 + 0.8 * calm + 0.6 * nostalgia + 0.2 * lift - 0.2 * tension))

    extension = _weighted_choice(options)
    return _apply_extension_to_roman(roman_seq, extension)





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
            if k in emotion_bias:
                emotion_score += (emotion_bias.get(k, 0.0) * pattern_emotion_score.get(k, 0.0))
        
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
            if emotion in emotion_bias:
                emotion_bias[emotion] = min(max(emotion_bias[emotion] + bias_delta[emotion] , 0.0 ), 1.0) # normalized updated bias

    weights:list[float] = []
    progression_patterns:list[ProgressionSummary] = [] 

    weights, progression_patterns = get_effective_weights(emotion_bias , progression_pattern_summary, section_attributes , exclude)
    if not progression_patterns or not weights or sum(weights) == 0:
        weights, progression_patterns = get_effective_weights(emotion_bias, progression_pattern_summary, {}, exclude)

    chosen_progression_summary:ProgressionSummary = random.choices(progression_patterns, weights, k=1)[0]

    result:list[str] = []

    for i in range(len(chosen_progression_summary["function_sequence"])):
        function_seq = chosen_progression_summary["function_sequence"][i]
        roman_seq = chosen_progression_summary['roman_sequence'][i]
        result.append(
            choose_extension(
                roman_seq=roman_seq,
                function=function_seq,
                mode=chosen_progression_summary.get("mode", "major"),
                emotion_bias=emotion_bias,
            )
        )


    
    return result , chosen_progression_summary['roman_sequence']




def get_all_section_progression(prompt_emotion_bias, progression_pattern_summary)->list[str]:
    sections_chord_prog:list[str] = []
    previous_chord_prog:list[str] = []
    for _, section_attributes in SECTION_CONFIG.items():
        chord_prog_with_extensions , chord_prog =  get_chord_prog(section_attributes,prompt_emotion_bias, progression_pattern_summary, previous_chord_prog)
        previous_chord_prog = chord_prog
        sections_chord_prog.extend(chord_prog_with_extensions)


    print(sections_chord_prog)

    return sections_chord_prog
