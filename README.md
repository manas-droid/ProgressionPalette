# AI-Assisted Chord Progression Generation (v1)

## Version

**v1.0 - Harmonic Core (Frozen)**

This document defines the **final, frozen scope of Version 1** of the project.
All future work must build **on top of v1** without modifying its assumptions, data, or logic.

---

## Project Overview

This project explores the intersection of **AI and music theory** by generating **harmonically valid chord progressions** from **high-level emotional intent**.

Rather than composing full songs, melodies, or audio productions, the system focuses on a **narrow but musically meaningful task**:

> Translating abstract emotional intent into short, structured harmonic ideas grounded in real musical data.

The system is designed as an **assistive creativity tool**, not an autonomous composer.

---

## Problem Statement (v1)

Given a simple emotional prompt (e.g., *“soothing”*, *“sad”*, *“tense”*), generate a **harmonically coherent 4-bar chord progression** that:

* Is musically valid within tonal harmony
* Reflects the requested emotional intent
* Is drawn from real musical practice
* Produces **different valid outputs** for the same prompt across runs

The system explicitly models **local harmonic intent**, not full song-level emotional narratives.

---

## Core Design Principles

### 1. Symbolic, Theory-Driven Generation

All generation is performed using **symbolic representations**:

* Roman numerals
* Harmonic functions (Tonic / Predominant / Dominant)
* Keys and modes (major / minor)

No audio, melody, rhythm, or production features are used for decision-making.

---

### 2. Data-Grounded Harmony

Chord progressions are derived from a **real musical corpus** (MusicXML lead-sheet style data), not invented arbitrarily.

Harmonic structure is treated as:

* finite
* enumerable
* statistically describable

---

### 3. Emotion as Compatibility, Not Truth

Emotions are modeled as **compatibility biases** over harmonic structure, not as objective or universal labels.

The system does **not** claim:

* emotional correctness
* listener perception accuracy
* psychological grounding

---

### 4. Controlled Diversity

The system produces variation through **probabilistic sampling**, not deterministic selection.

Higher-probability patterns appear more often, but lower-probability patterns remain possible.

---

## Dataset (v1)

### Source

* 205 MusicXML songs
* Lead-sheet-style harmony
* Global key and mode per song

### Extraction Rules

* 4 bars per progression
* Exactly 1 chord per bar
* Global key and mode inherited from song
* Only **diatonic** chords considered
* If a bar contains multiple chords, the **first diatonic chord** is selected
* Chord extensions, suspensions, and added tones are stripped
* Only basic triads (major, minor, diminished) are retained
* Non-diatonic bars invalidate the 4-bar window

### Dataset Size

* 1056 extracted progressions (non-unique)
* Deduplicated into a **progression pattern catalog**
* Each pattern assigned a frequency-derived base weight

---

## Data Representation

### Progression Pattern (Conceptual)

* Roman numeral sequence (length = 4)
* Harmonic function sequence
* Mode (major / minor)
* Empirical base weight
* Emotion compatibility scores
* Source provenance (song + measure index)

### Key Profile

* Tonic
* Mode
* Sampling weight (bias toward common keys)

---

## Emotion Modeling (v1)

### Emotion Space (Fixed)

* suspenseful_tense
* calm_meditative
* wistful_longing
* motivational_triumphant
* nostalgic_sentimental
* dark_brooding
* happy_uplifting

### Emotion Scores

Each progression pattern is assigned **heuristic compatibility scores** based on:

* tonic / predominant / dominant balance
* cadence strength
* mode
* diminished harmony presence

These scores are **precomputed** and stored with the dataset.

---

## Prompt Handling (v1)

User input is mapped to emotion biases using **predefined prompt presets**.

Example:

```
"soothing" : calm_meditative , nostalgic_sentimental
```

This layer is intentionally simple and exists to validate the core generation pipeline.
It is designed to be replaced by more flexible natural-language interpretation in future versions.

---

## Generation Pipeline (v1)

1. **Prompt -> Emotion Bias Vector**
2. **Pattern Filtering** (by mode)
3. **Effective Weight Computation**

   ```
   effective_weight =
       base_weight
     × emotion_compatibility
     × motion_penalty
   ```
4. **Weighted Sampling** of one progression pattern
5. **Key Sampling** from key profile
6. **Roman → Chord Realization**
7. **Playback as Block-Chord MIDI**

---

## Output Specification

### Symbolic Output

* Selected key
* 4-bar chord progression
* One chord per bar

Example:

```
Key: C minor
Progression:
1 | Cm
2 | Cm
3 | Fm
4 | Cm
```

### Audio Output

* MIDI file
* Fixed tempo
* Piano instrument
* Block triads (no inversions, no rhythm modeling)

Audio playback is for **demonstration only**.

---

## What v1 Explicitly Does NOT Do

* No melody generation
* No rhythm or groove modeling
* No modulation detection
* No chord extensions in structure
* No neural harmony generation
* No emotional classification of audio
* No song-level form modeling

These are **intentional exclusions**, not limitations.

---

## Status: Version Frozen

Version 1 is **complete and frozen**.

* Dataset locked
* Extraction rules locked
* Generation logic locked
* Playback scope locked

All future work must be implemented as **additive extensions** that do not modify v1 behavior.

---

## Looking Ahead

Future versions may introduce:

* Natural language prompt interpretation
* Harmonic decoration at playback time
* Explainability (“why this progression?”)
* Multi-section progression chaining

These extensions will preserve the **v1 harmonic core**.

---

## Final Note

Version 1 demonstrates that **emotion-conditioned harmonic generation** can be achieved through:

* careful abstraction
* music-theory grounding
* real musical data
* probabilistic reasoning

without relying on black-box generative models.