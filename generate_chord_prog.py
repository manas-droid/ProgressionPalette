from dataclasses import dataclass
import json
from typing import Literal, TypedDict
import random
from pathlib import Path
from music21 import key as m21key, roman, stream, tempo, meter, instrument
import subprocess

emotion = input("Enter the emotion: ")

@dataclass(frozen=True)
class EmotionScore(TypedDict):
    suspenseful_tense: float
    calm_meditative: float
    wistful_longing: float
    motivational_triumphant: float
    nostalgic_sentimental: float
    dark_brooding: float
    happy_uplifting: float


@dataclass(frozen=True)
class ProgressionSummary(TypedDict):
    roman_sequence:list[str]
    mode: Literal['minor', 'major']
    function_sequence: list[str]
    count : int
    base_weight: float
    emotion_scores: EmotionScore


@dataclass(frozen=True)
class KeyProfile(TypedDict):
    key_id:str
    tonic:str
    mode:Literal['major', 'minor']
    display_name:str
    weight : float

def get_effective_weights(progression_pattern_summary: list[ProgressionSummary] , prompt_emotion_bias: EmotionScore)->tuple[list[float], list[ProgressionSummary]]:
    result:list[float] = []
    positive_weighted_pattern:list[ProgressionSummary] = []
    for pattern in progression_pattern_summary:
        pattern_emotion_score = pattern['emotion_scores']
        emotion_score:float = 0.0
        
        for k in pattern_emotion_score.keys():
            if prompt_emotion_bias.get(k):
                emotion_score += (prompt_emotion_bias.get(k) * pattern_emotion_score.get(k))
        
        motion_penalty: float = len(set(pattern['roman_sequence'])) / len(pattern['roman_sequence'])

        effective_weight:float = emotion_score * pattern['base_weight'] * motion_penalty

        if effective_weight > 0:
            result.append(effective_weight)
            positive_weighted_pattern.append(pattern)

    return result , positive_weighted_pattern


def build_midi_progression(
    roman_sequence: list[str],
    key_choice: KeyProfile,
    output_path: Path,
    bpm: int = 75,
) -> stream.Score:
    key_signature = m21key.Key(key_choice["tonic"], key_choice["mode"])
    part = stream.Part()
    part.append(instrument.Piano())
    part.append(tempo.MetronomeMark(number=bpm))
    part.append(meter.TimeSignature("4/4"))
    part.append(key_signature)

    for numeral in roman_sequence:
        rn = roman.RomanNumeral(numeral, key_signature)
        rn.quarterLength = 4
        rn.writeAsChord = True
        for p in rn.pitches:
            p.octave = 4

        part.append(rn)

    score = stream.Score()
    score.append(part)
    score.write("midi", fp=str(output_path))
    return score




with open('prompt_presets.json', mode='r') as file:
    prompt_presets = json.load(file)

with open('progression_pattern_summary.json', mode='r') as file:
    progression_pattern_summary:list[ProgressionSummary]= json.load(file)


with open('key_profile.json', mode='r') as file:
    key_profile: list[KeyProfile] = json.load(file)



if not prompt_presets.get(emotion):
    emotion = 'neutral'




prompt_emotion_bias:EmotionScore = prompt_presets.get(emotion)



weights , positive_weighted_pattern = get_effective_weights(progression_pattern_summary, prompt_emotion_bias)

if not weights or sum(weights) == 0:
    print("  ------- effective weight overall is zero, therefore implementing fallback ------- ")
    weights = [p['base_weight'] for p in progression_pattern_summary]
    positive_weighted_pattern = progression_pattern_summary


choose_pattern : ProgressionSummary = random.choices(positive_weighted_pattern, weights, k=1)[0]




mode = choose_pattern['mode']

filtered_key_profile = [key for key in key_profile if key['mode'] == mode]


key_choice = random.choices(filtered_key_profile, weights=[key['weight'] for key in filtered_key_profile] , k = 1)[0]



output_path = Path("generated_progression.mid")

score = build_midi_progression(choose_pattern["roman_sequence"], key_choice, output_path, bpm=150)

print(f"Wrote MIDI to {output_path}")
subprocess.run(
    ["/usr/bin/fluidsynth", "-ni", "/usr/share/sounds/sf2/default-GM.sf2", str(output_path)],
    check=False,
)
