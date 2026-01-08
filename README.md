# AI-Assisted Chord Progression Generation from Emotional Prompts

## Project Overview

This project explores the intersection of **artificial intelligence and music theory** by building a system that generates **harmonically valid chord progressions** from **natural-language emotional prompts**.

Rather than composing full songs, melodies, or audio, the system focuses on a narrowly defined but musically meaningful task:

> Translating abstract human emotional intent (e.g., *“sad”*, *“soothing”*, *“hopeful”*) into short, structured harmonic ideas.

The project is designed as an **assistive creativity tool** that complements human musicianship rather than replacing it.

---

## Problem Statement (Locked)

Musicians often think in high-level emotional or situational terms, while music theory operates on structured harmonic rules. Translating vague emotional intent into concrete, musically valid chord progressions typically requires theoretical knowledge and experimentation.

**The problem addressed by this project is:**

> Given a natural-language emotional or situational prompt, generate a **harmonically coherent four-bar chord progression** that is compatible with the requested emotion, while respecting basic principles of tonal harmony.

The system must be capable of generating **multiple distinct but valid progressions** for the same prompt, reflecting the non-uniqueness of musical interpretation.

---

## System Scope

### What the System Does

* Accepts **natural-language emotional prompts** (e.g., *“soothing”*, *“sad”*, *“reflective”*)
* Generates a **4-bar chord progression**

  * Exactly **one chord per bar**
  * All chords belong to a **single tonal context**
* Produces **multiple valid outputs** for the same prompt via controlled sampling
* Ensures **harmonic validity** using music-theory constraints
* Plays the generated chords for **demonstration and verification purposes**

---

### What the System Does NOT Do

This project intentionally does **not** attempt to:

* Generate melodies
* Generate lyrics
* Perform audio synthesis or production
* Model rhythm, tempo, or groove
* Generate full song structures (verse/chorus/bridge)
* Infer or model song-level emotional arcs
* Claim emotional correctness or listener perception accuracy
* Learn emotion labels from large audio or lyric datasets

These exclusions are **deliberate design choices**, not limitations.

---

## Core Design Principles

### 1. Local Harmonic Intent, Not Full Composition

The system models **local harmonic plausibility**, not complete musical narratives.

A “sad” chord progression is defined as:

* Harmonically compatible with sadness
* Commonly used in sad musical contexts
* Not emotionally contradictory

It does **not** imply that:

* Every progression in a sad song must be sad
* Emotional interpretation is universal or objective

---

### 2. Symbolic, Theory-Driven Representation

The system operates entirely on **symbolic music representations**:

* Chord symbols
* Roman numerals
* Harmonic functions (tonic, predominant, dominant)

Audio playback exists only to demonstrate that generated progressions are **musically meaningful and playable**.

---

### 3. Controlled Diversity, Not Randomness

The same emotional prompt should yield **different outputs across runs**, but all outputs must remain:

* Harmonically valid
* Emotionally compatible
* Consistent with the system’s constraints

This diversity is achieved through **probabilistic sampling within a constrained harmonic space**, not unconstrained randomness.

---

### 4. Explicit Abstraction Boundaries

The project intentionally avoids:

* Automatic modulation detection
* Secondary dominant inference
* Chord extension modeling at the structural level

These phenomena are musically important but are outside the scope of the current abstraction, which prioritizes **clarity, explainability, and correctness**.

---

## Output Specification

Each generated result includes:

* A **key and mode** (major or minor)
* A **4-bar chord progression**
* One chord per bar
* Chords expressed as **basic triads** (major, minor, diminished)

Example output format:

```
Key: C Major
Bars:
1. C
2. Am
3. F
4. G
```

---

## Project Philosophy

This project prioritizes:

* **Interpretability over black-box learning**
* **Musical correctness over expressive excess**
* **Depth over breadth**
* **Clear abstractions over maximal realism**

The system is designed to be **small enough to understand** and **rigorous enough to defend**.
---