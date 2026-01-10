from dataclasses import dataclass
from typing import Literal, TypedDict


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
