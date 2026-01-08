
from pathlib import Path
import json
from music21 import converter, key as m21key, stream, pitch as m21pitch, note as m21note, chord as m21chord



ROMAN_MAJOR = {
    1: "I", 2: "ii", 3: "iii", 4: "IV", 5: "V", 6: "vi", 7: "vii°"
}

ROMAN_MINOR = {
    1: "i", 3: "III", 4: "iv", 5: "V", 6: "VI", 7: "VII"
}

FUNCTION_MAP = {
    "I": "T", "i": "T",
    "iii": "T", "vi": "T",
    "IV": "PD", "iv": "PD", "ii": "PD",
    "V": "D", "vii°": "D", "VII": "D"
}


def find_musicxml_files(root: Path) -> list[Path]:
    xml_files: list[Path] = []
    for folder in root.rglob("all-musicxml"):
        if not folder.is_dir():
            continue
        xml_files.extend(folder.rglob("*musicXML.xml"))
    return sorted(set(xml_files))


def analyze_key(score: stream.Score) -> m21key.Key:
    return score.analyze("key")


def build_diatonic_triads(k: m21key.Key) -> dict[int, set[int]]:
    scale = k.getScale()
    triads: dict[int, set[int]] = {}
    for degree in range(1, 8):
        pitches = [
            scale.pitchFromDegree(degree),
            scale.pitchFromDegree(((degree + 1) % 7) + 1),
            scale.pitchFromDegree(((degree + 3) % 7) + 1),
        ]
        triads[degree] = {p.pitchClass for p in pitches}
    return triads


def collect_measure_pitches(score: stream.Score) -> dict[int, list[m21pitch.Pitch]]:
    measures: dict[int, list[m21pitch.Pitch]] = {}
    for part in score.parts:
        for meas in part.getElementsByClass(stream.Measure):
            num = meas.number
            if num is None:
                continue
            measures.setdefault(num, [])
            for element in meas.recurse():
                if isinstance(element, m21note.Note):
                    measures[num].append(element.pitch)
                elif isinstance(element, m21chord.Chord):
                    measures[num].extend(element.pitches)
    return measures


def measure_to_degree(
    pitches: list[m21pitch.Pitch],
    triads: dict[int, set[int]],
) -> int | None:
    if not pitches:
        return None
    pitch_classes = {p.pitchClass for p in pitches}
    best_degree = None
    best_overlap = 0
    for degree, triad_pcs in triads.items():
        overlap = len(pitch_classes & triad_pcs)
        if overlap > best_overlap:
            best_overlap = overlap
            best_degree = degree
    if best_overlap == 0:
        return None
    return best_degree


def degree_to_roman_and_function(degree: int, mode: str) -> tuple[str, str] | None:
    roman_map = ROMAN_MAJOR if mode == "major" else ROMAN_MINOR
    roman = roman_map.get(degree)
    if not roman:
        return None
    function = FUNCTION_MAP.get(roman)
    if not function:
        return None
    return roman, function


def extract_progressions(score: stream.Score, source: Path) -> list[dict]:
    key_obj = analyze_key(score)
    mode = key_obj.mode
    triads = build_diatonic_triads(key_obj)

    measures = collect_measure_pitches(score)
    ordered_measures = sorted(measures.keys())



    degrees_by_measure: list[tuple[int, int]] = []
    for num in ordered_measures:
        degree = measure_to_degree(measures[num], triads)
        if degree is not None:
            degrees_by_measure.append((num, degree))

    progressions: list[dict] = []
    for idx in range(len(degrees_by_measure) - 3):
        window = degrees_by_measure[idx:idx + 4]
        measure_numbers = [m for m, _ in window]
        if measure_numbers != list(range(measure_numbers[0], measure_numbers[0] + 4)):
            continue
        roman_seq = []
        function_seq = []
        valid = True
        for _, degree in window:
            mapped = degree_to_roman_and_function(degree, mode)
            if not mapped:
                valid = False
                break
            roman, function = mapped
            roman_seq.append(roman)
            function_seq.append(function)
        if not valid:
            continue
        progressions.append({
            "source_file": str(source),
            "key": key_obj.tonic.name,
            "mode": mode,
            "start_measure": measure_numbers[0],
            "roman_sequence": roman_seq,
            "function_sequence": function_seq,
        })
    return progressions


EMOTIONAL_PROFILE = [
    {
        "emotion_id": "suspenseful_tense",
        "name": "suspenseful and tense",
        "valence": -1,
        "energy": 2,
        "tension": 3,
        "resolution_preference": "unresolved",
        "mode_preference": "either",
        "description": "Dominant-heavy motion, unresolved endings, and diminished color.",

    },
    {
        "emotion_id": "calm_meditative",
        "name": "calm and meditative",
        "valence": 1,
        "energy": 0,
        "tension": 0,
        "resolution_preference": "resolved",
        "mode_preference": "either",
        "description": "Stable tonics, gentle predominant motion, low dominant pressure.",
    },
    {
        "emotion_id": "wistful_longing",
        "name": "wistful and longing",
        "valence": -1,
        "energy": 1,
        "tension": 1,
        "resolution_preference": "either",
        "mode_preference": "minor",
        "description": "Minor-mode color with softer cadences and reflective movement.",
    },
    {
        "emotion_id": "motivational_triumphant",
        "name": "motivational and triumphant",
        "valence": 2,
        "energy": 3,
        "tension": 2,
        "resolution_preference": "resolved",
        "mode_preference": "major",
        "description": "Major-mode drive with strong cadences and dominant emphasis.",

    },
    {
        "emotion_id": "nostalgic_sentimental",
        "name": "nostalgic and sentimental",
        "valence": 0,
        "energy": 1,
        "tension": 1,
        "resolution_preference": "either",
        "mode_preference": "either",
        "description": "Warm stability with mild tension; avoids strong finality.",
    },
    {
        "emotion_id": "dark_brooding",
        "name": "dark and brooding",
        "valence": -2,
        "energy": 1,
        "tension": 2,
        "resolution_preference": "unresolved",
        "mode_preference": "minor",
        "description": "Minor-mode gravity with diminished or dominant pull.",
    },
    {
        "emotion_id": "happy_uplifting",
        "name": "happy and uplifting",
        "valence": 2,
        "energy": 2,
        "tension": 1,
        "resolution_preference": "resolved",
        "mode_preference": "major",
        "description": "Major-mode brightness with tonic stability and clean cadences.",
    },
]


def _cadence_strength(function_seq: list[str]) -> float:
    if len(function_seq) < 2:
        return 0.0
    if function_seq[-2:] == ["D", "T"]:
        return 1.0
    if function_seq[-1] == "T":
        return 0.5
    return 0.0


def score_emotions(roman_seq: list[str], function_seq: list[str], mode: str) -> dict[str, float]:
    tonic_count = function_seq.count("T")
    predominant_count = function_seq.count("PD")
    dominant_count = function_seq.count("D")
    ending_tonic = function_seq[-1] == "T" if function_seq else False
    ending_dominant = function_seq[-1] == "D" if function_seq else False
    has_diminished = "vii°" in roman_seq
    cadence = _cadence_strength(function_seq)
    major_mode = mode == "major"
    minor_mode = mode == "minor"

    raw_scores: dict[str, float] = {}
    raw_scores["suspenseful_tense"] = (
        0.5 * dominant_count
        + (1.0 if ending_dominant else 0.0)
        + (0.5 if has_diminished else 0.0)
        - 0.2 * tonic_count
    )
    raw_scores["calm_meditative"] = (
        0.6 * tonic_count
        + 0.3 * predominant_count
        + (0.5 if ending_tonic else 0.0)
        - 0.4 * dominant_count
        - (0.3 if has_diminished else 0.0)
    )
    raw_scores["wistful_longing"] = (
        (1.0 if minor_mode else 0.2)
        + 0.2 * predominant_count
        + (0.2 if ending_tonic else 0.0)
        - 0.2 * dominant_count
    )
    raw_scores["motivational_triumphant"] = (
        (1.0 if major_mode else 0.0)
        + 0.4 * dominant_count
        + 0.6 * cadence
        - 0.2 * predominant_count
    )
    raw_scores["nostalgic_sentimental"] = (
        0.3 * tonic_count
        + 0.2 * predominant_count
        + (0.3 if ending_tonic else 0.0)
        + (0.3 if minor_mode else 0.1)
        - 0.3 * dominant_count
    )
    raw_scores["dark_brooding"] = (
        (1.0 if minor_mode else 0.0)
        + (0.6 if has_diminished else 0.0)
        + 0.2 * dominant_count
        - 0.2 * tonic_count
    )
    raw_scores["happy_uplifting"] = (
        (1.0 if major_mode else 0.0)
        + 0.4 * tonic_count
        + 0.3 * cadence
        - 0.3 * dominant_count
        - (0.2 if has_diminished else 0.0)
    )

    clipped_scores = {k: max(v, 0.0) for k, v in raw_scores.items()}
    total = sum(clipped_scores.values())
    if total == 0:
        equal = 1.0 / len(clipped_scores)
        return {k: equal for k in clipped_scores}
    return {k: round(v / total, 4) for k, v in clipped_scores.items()}


def collect_all_progressions(root: Path) -> list[dict]:
    all_progressions: list[dict] = []
    for xml_file in find_musicxml_files(root):
        try:
            score = converter.parse(str(xml_file))
        except Exception:
            continue
        all_progressions.extend(extract_progressions(score, xml_file))
    return all_progressions


def build_emotion_scores(progressions: list[dict]) -> list[dict]:
    scored: list[dict] = []
    for prog in progressions:
        scores = score_emotions(
            prog["roman_sequence"],
            prog["function_sequence"],
            prog["mode"],
        )
        scored.append({
            "source_file": prog["source_file"],
            "key": prog["key"],
            "mode": prog["mode"],
            "start_measure": prog["start_measure"],
            "roman_sequence": prog["roman_sequence"],
            "function_sequence": prog["function_sequence"],
            "emotion_scores": scores,
            "weight": 0  # the probability bias for choosing a chord progression pattern during generation.
        })
    return scored


def update_progression_weights(records: list[dict]) -> list[dict]:
    counts: dict[tuple[str, ...], int] = {}
    for item in records:
        seq = tuple(item.get("roman_sequence", []))
        counts[seq] = counts.get(seq, 0) + 1
    max_count = max(counts.values()) if counts else 1
    print("max count", max_count)
    for item in records:
        seq = tuple(item.get("roman_sequence", []))
        count = counts.get(seq, 0)
        item["weight"] = round(count / max_count, 2)
    return records


def update_weights_file(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    update_progression_weights(records)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)


def main() -> None:
    root = Path.cwd()

    progressions = collect_all_progressions(root)

    emotion_scores = build_emotion_scores(progressions)
    update_progression_weights(emotion_scores)
    emotion_scores_path = root / "chord_progression_with_emotion_score.json"
    with emotion_scores_path.open("w", encoding="utf-8") as handle:
        json.dump(emotion_scores, handle, indent=2)

    print(
        "Wrote "
        f"{len(emotion_scores)} scored progressions to {emotion_scores_path}"
    )


if __name__ == "__main__":
    main()
