from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any, Dict, List, Tuple

EMOTIONS = [
    "suspenseful_tense",
    "calm_meditative",
    "wistful_longing",
    "motivational_triumphant",
    "nostalgic_sentimental",
    "dark_brooding",
    "happy_uplifting",
]

MODIFIERS = {
    "extremely": 1.5,
    "very": 1.3,
    "somewhat": 0.8,
    "slightly": 0.6,
    "a bit": 0.6,
}

LEXICON_PATH = Path(__file__).resolve().parent / "phrase_lexicon.json"


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\\s]", " ", lowered)
    lowered = re.sub(r"\\s+", " ", lowered).strip()
    return lowered


def _load_lexicon() -> Dict[str, Dict[str, float]]:
    with LEXICON_PATH.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    lexicon: Dict[str, Dict[str, float]] = {}
    for phrase, contribs in raw.items():
        cleaned = _normalize_text(phrase)
        lexicon[cleaned] = {k: float(v) for k, v in contribs.items() if k in EMOTIONS}
    return lexicon


LEXICON = _load_lexicon()




def _neutral_bias() -> Dict[str, float]:
    return {emotion: 0.3 for emotion in EMOTIONS}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def prompt_to_emotion_bias(prompt: str) -> Tuple[Dict[str, float], Dict[str, Any]]:
    normalized = _normalize_text(prompt)
    tokens = normalized.split() if normalized else []
    phrases = sorted(LEXICON.keys(), key=lambda p: len(p.split()), reverse=True)

    modifier_tokens = {tuple(k.split()): v for k, v in MODIFIERS.items()}
    modifier_lengths = sorted({len(k) for k in modifier_tokens}, reverse=True)

    bias: Dict[str, float] = {emotion: 0.0 for emotion in EMOTIONS}
    matched_phrases: List[Dict[str, Any]] = []
    applied_modifiers: List[Dict[str, Any]] = []
    ignored_modifiers: List[str] = []
    pending_modifier: Tuple[str, float] | None = None

    index = 0
    while index < len(tokens):
        modifier_applied = False
        for length in modifier_lengths:
            if index + length > len(tokens):
                continue
            window = tuple(tokens[index:index + length])
            if window in modifier_tokens:
                if pending_modifier is None:
                    pending_modifier = (" ".join(window), modifier_tokens[window])
                else:
                    print("Modifier ignored because it is probably repeated")
                    ignored_modifiers.append(" ".join(window))
                index += length
                modifier_applied = True
                break
        if modifier_applied:
            continue

        phrase_match = None
        phrase_len = 0
        for phrase in phrases:
            phrase_tokens = phrase.split()
            if tokens[index:index + len(phrase_tokens)] == phrase_tokens:
                phrase_match = phrase
                phrase_len = len(phrase_tokens)
                break

        if phrase_match:
            multiplier = 1.0
            modifier_label = None
            if pending_modifier:
                modifier_label, multiplier = pending_modifier
                pending_modifier = None
            contribs = LEXICON.get(phrase_match, {})
            for emotion, value in contribs.items():
                bias[emotion] += max(0.0, value * multiplier)
            matched_phrases.append(
                {
                    "phrase": phrase_match,
                    "multiplier": multiplier,
                    "start_index": index,
                }
            )
            if modifier_label:
                applied_modifiers.append(
                    {"modifier": modifier_label, "phrase": phrase_match, "multiplier": multiplier}
                )
            index += phrase_len
            continue

        index += 1

    if all(value == 0.0 for value in bias.values()):
        return _neutral_bias(), {
            "normalized_prompt": normalized,
            "tokens": tokens,
            "matched_phrases": matched_phrases,
            "applied_modifiers": applied_modifiers,
            "ignored_modifiers": ignored_modifiers,
            "final_bias": _neutral_bias(),
        }

    max_value = max(bias.values()) if bias else 1.0
    if max_value == 0:
        normalized_bias = _neutral_bias()
    else:
        normalized_bias = {k: _clamp(v / max_value) for k, v in bias.items()}

    debug_info = {
        "normalized_prompt": normalized,
        "tokens": tokens,
        "matched_phrases": matched_phrases,
        "applied_modifiers": applied_modifiers,
        "ignored_modifiers": ignored_modifiers,
        "final_bias": normalized_bias,
    }
    return normalized_bias, debug_info
