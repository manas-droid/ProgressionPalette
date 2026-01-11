# Emotion-Aware Chord Progression Generation

## Overview

This project explores the intersection of **AI and music theory** by building a system that generates **emotion-conditioned chord progressions** using symbolic music representations.

Rather than treating music generation as a black-box sequence problem, the system emphasizes:

* interpretable harmonic structure
* explicit emotion modeling
* modular, versioned evolution
* clear separation between *generation*, *structure*, and *playback*

The goal is to demonstrate how AI can **assist musical creativity** by producing harmonically meaningful, emotionally guided progressions that musicians can build upon.

---

## Core Capabilities

At its core, the system:

* accepts a **high-level emotional intent** (e.g., *calm*, *hopeful*, *tense*)
* maps it into a structured **emotion bias space**
* samples from a dataset of extracted chord progressions
* renders the result as **playable MIDI output**

All musical decisions are grounded in **explicit rules and data**, not opaque models.

---

## Implemented Features (by Version)

### v1 - Emotion-Conditioned Chord Progression Generation (Frozen)

**What it does**

* Generates a **single 4-bar chord progression**
* Uses Roman numeral harmony and functional labels (T / PD / D)
* Samples from a curated dataset of real music
* Conditions generation on an emotion bias vector

**Key ideas**

* No black-box ML
* Fully explainable weighting and sampling
* Deterministic structure with stochastic variety

---

### v2.1 - Safe Natural Language Prompt Interpretation (Frozen)

**What it does**

* Converts short natural language prompts into emotion bias vectors
* Uses a phrase-based lexicon with intensity modifiers (e.g., *very*, *slightly*)
* Avoids embeddings or large language models

**Why it matters**

* Keeps interpretation transparent
* Prevents hallucinated semantics
* Provides a clean interface between language and music

---

### v2.5 - Section-Aware Harmonic Generation (Frozen)

**What it does**

* Extends generation from one 4-bar progression to **structured sections**
* Supports:

  * Intro
  * Verse
  * Chorus
* All sections share a **global key and mode**, chosen once from the initial emotion

**How it works**

* Each section applies:

  * small emotion bias adjustments
  * harmonic constraints (motion, cadence, dominant usage)
* Sections are generated independently but stitched coherently

**What it is not**

* Not full song composition
* No melody, rhythm, or modulation
* No user-defined emotional arcs

---

### v2.3 - Harmonic Decoration at Playback Time (Frozen)

**What it does**

* Improves **audible richness** without changing harmonic structure
* Applies light, probabilistic decoration at playback time:

  * sevenths
  * inversions
  * octave doubling
  * optional arpeggiation

**Design rule**

* Decoration never affects:

  * progression selection
  * emotion scoring
  * section structure

This layer exists purely to make output **sound more musical**, not to change decisions.

---

## Experimental / Advanced Features

### Emotion-Aware Harmonic Decoration (Experimental, v3+)

An experimental extension conditions chord **color and extensions** on higher-level emotional axes such as:

* tension
* warmth
* lift

This enables:

* richer dominant alterations
* emotion-sensitive harmonic color
* expressive variation without changing function

This feature is **intentionally excluded from frozen v2.3** and reserved for future versions.

---

## Output

The system produces:

* **Symbolic output**

  * Roman numeral sequences
  * Section labels
* **Playable audio**

  * MIDI files
  * Rendered via software synthesis (e.g., FluidSynth)

The output is intended as a **harmonic sketch**, not a finished composition.

---

## Design Philosophy

Key principles guiding the project:

* **Explainability over opacity**
* **Music theory as structure, not decoration**
* **Incremental, versioned evolution**
* **Separation of concerns**

  * emotion → harmony → structure → sound

Each version introduces *one meaningful idea* and freezes it before moving on.

---

## Future Work

Planned or potential extensions include:

* User-directed emotional arcs per section
* Key modulation and modal mixture
* Emotion-aware harmonic decoration (formalized)
* Melody-conditioned harmony
* More expressive rhythmic realization
* Embedding-based or LLM-assisted prompt interpretation
* Interactive or adaptive generation workflows

All future work will preserve the frozen behavior of earlier versions.

---

## Summary

This project demonstrates that **emotion-guided musical structure** can be modeled using:

* interpretable representations
* data-derived harmonic patterns
* lightweight probabilistic reasoning

without relying on black-box generative models.

The system is designed to **complement human creativity**, not replace it.