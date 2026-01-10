import json
import random
import subprocess
from pathlib import Path

from music21 import instrument, key as m21key, meter, roman, stream, tempo

from chord_generation_model import EmotionScore, KeyProfile, ProgressionSummary
from nlp.matcher import prompt_to_emotion_bias
from section_chord_prog_gen import get_all_section_progression

FLUIDSYNTH_PATH = "/usr/bin/fluidsynth"
SOUNDFONT_PATH = "/usr/share/sounds/sf2/default-GM.sf2"
DEFAULT_BPM = 150  # keep fixed in 70–80 range


def get_effective_weights(
    progression_pattern_summary: list[ProgressionSummary],
    prompt_emotion_bias: EmotionScore,
) -> tuple[list[float], list[ProgressionSummary]]:
    weights: list[float] = []
    candidates: list[ProgressionSummary] = []

    for pattern in progression_pattern_summary:
        pattern_emotion_score = pattern["emotion_scores"]
        emotion_score = 0.0
        for emotion_id in pattern_emotion_score.keys():
            emotion_score += (
                prompt_emotion_bias.get(emotion_id, 0.0) * pattern_emotion_score.get(emotion_id, 0.0)
            )

        motion_penalty = len(set(pattern["roman_sequence"])) / len(pattern["roman_sequence"])
        effective_weight = emotion_score * pattern["base_weight"] * motion_penalty
        if effective_weight > 0:
            weights.append(effective_weight)
            candidates.append(pattern)

    return weights, candidates


def build_midi_progression(
    roman_sequence: list[str],
    key_choice: KeyProfile,
    output_path: Path,
    bpm: int = DEFAULT_BPM,
) -> None:
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


def play_midi_file(midi_path: Path) -> None:
    try:
        subprocess.run(
            [FLUIDSYNTH_PATH, "-ni", SOUNDFONT_PATH, str(midi_path)],
            check=False,
        )
    except FileNotFoundError:
        print(f"Cannot run fluidsynth at {FLUIDSYNTH_PATH}; MIDI saved at {midi_path}.")


def load_data() -> tuple[list[ProgressionSummary], list[KeyProfile]]:
    with open("progression_pattern_summary.json", mode="r", encoding="utf-8") as file:
        progression_pattern_summary: list[ProgressionSummary] = json.load(file)
    with open("key_profile.json", mode="r", encoding="utf-8") as file:
        key_profile: list[KeyProfile] = json.load(file)
    return progression_pattern_summary, key_profile


def choose_key(
    mode: str,
    key_profile: list[KeyProfile],
) -> KeyProfile:
    filtered_key_profile = [key for key in key_profile if key["mode"] == mode]
    return random.choices(
        filtered_key_profile,
        weights=[key["weight"] for key in filtered_key_profile],
        k=1,
    )[0]


def run_once(
    prompt: str,
    progression_pattern_summary: list[ProgressionSummary],
    key_profile: list[KeyProfile],
    midi_path: Path,
) -> None:
    prompt_emotion_bias, debug_info = prompt_to_emotion_bias(prompt)
    weights, candidates = get_effective_weights(progression_pattern_summary, prompt_emotion_bias)

    if not weights or sum(weights) == 0:
        print("------- no strong matches; using fallback weights -------")
        candidates = progression_pattern_summary
        weights = [p["base_weight"] for p in progression_pattern_summary]

    chosen_pattern: ProgressionSummary = random.choices(candidates, weights, k=1)[0]
    key_choice = choose_key(chosen_pattern["mode"], key_profile)

    final_chord_progression = get_all_section_progression(prompt_emotion_bias, progression_pattern_summary)

    build_midi_progression(final_chord_progression, key_choice, midi_path, bpm=DEFAULT_BPM)
    print(f"Wrote MIDI to {midi_path}")
    play_midi_file(midi_path)


def main() -> None:
    progression_pattern_summary, key_profile = load_data()
    midi_path = Path("generated_progression.mid")

    print("Enter an emotion prompt (or 'q' to quit).")
    while True:
        prompt = input("Emotion prompt> ").strip()
        if prompt.lower() in {"q", "quit", "exit"}:
            break
        if not prompt:
            continue
        run_once(prompt, progression_pattern_summary, key_profile, midi_path)


if __name__ == "__main__":
    main()
