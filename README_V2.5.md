
## Summary

Version 2.5 demonstrates that:

> Short, emotionally conditioned harmonic ideas can be structured into musically meaningful sections using theory-informed constraints, without introducing black-box models or full song complexity.

---

## Purpose of v2.5

Version 2.5 extends the system from generating a **single 4-bar chord progression** to generating a **structured multi-section harmonic sketch**, while preserving the symbolic, data-driven harmonic core defined in v1.

The goal is **structural musical coherence**, not full song composition.

---

## What v2.5 Adds

v2.5 introduces **section-aware generation**, allowing the system to produce multiple short chord progressions arranged into musically meaningful sections such as:

* Intro
* Verse
* Chorus

Each section is generated independently using the existing v1 generator, but with **section-specific constraints and bias adjustments** that reflect its musical role.

---

## What v2.5 Does NOT Do

v2.5 explicitly does **not** include:

* melody generation
* rhythm or groove modeling
* lyrics or text alignment
* modulation or key changes
* user-specified emotional arcs per section
* full song form learning

These are intentional exclusions and are deferred to later versions.

---

## Global Tonal Policy (Locked)

### Key & Mode Selection

* The **global mode (major/minor)** is determined **once**, based solely on the **initial prompt’s emotion bias**.
* The **global key (tonic)** is sampled once from a weighted key profile constrained by the chosen mode.
* All sections are generated **within the same key and mode**.

Section-level bias adjustments **must not** affect key or mode selection.

---

## Section Template Overview

v2.5 supports exactly **three fixed sections**, each consisting of **4 bars**:

1. **Intro** - establishes tonal and emotional space
2. **Verse** - explores harmonic motion
3. **Chorus** - provides resolution or emphasis

Sections are ordered as:

```
Intro -> Verse -> Chorus
```

No additional sections are supported in v2.5.

---

## Section Generation Model

Each section is generated using the following process:

1. Start from the **base emotion bias** derived from the user prompt (v2.1).
2. Apply a **small, section-specific bias delta**.
3. Filter progression patterns using **section-specific harmonic constraints**.
4. Compute effective weights using the v1 weighting formula.
5. Sample one 4-bar progression.
6. Realize all sections in the same global key.

Sections are **independent in sampling** but **coherent in tonality**.

---

## Section Constraint Definitions (Frozen)

### Intro Section

**Musical role:**
Establish stability and mood without strong tension.

**Constraints:**

* Motion <= 0.50
* Dominant count <= 1
* Must not end on dominant

**Bias adjustment:**

```json
{
  "suspenseful_tense": -0.2,
  "dark_brooding": -0.1,
  "calm_meditative": +0.1
}
```

---

### Verse Section

**Musical role:**
Develop harmonic space without strong closure.

**Constraints:**

* 0.50 < Motion <= 0.75
* Dominant count <= 2

**Bias adjustment:**
None (uses base emotion bias unchanged)

---

### Chorus Section

**Musical role:**
Resolution, emphasis, or emotional peak.

**Constraints:**

* Motion >= 0.50
* Dominant count >= 1
* Must end on tonic

**Bias adjustment:**

```json
{
  "motivational_triumphant": +0.2,
  "happy_uplifting": +0.2
}
```

---

## Cross-Section Rules (Locked)

### 1. No Immediate Repetition

The same Roman numeral progression **must not appear in adjacent sections**.

### 2. Safe Fallback

If section constraints over-filter the dataset:

* The system falls back to unconstrained v1 generation for that section.
* Generation must never fail due to empty candidate sets.

### 3. Section Independence

Each section:

* is sampled independently
* uses its own filtered candidate pool
* shares the same global key and mode

---

## Output Format (v2.5)

### Symbolic Output

Example:

```
Key: G major

Intro (4 bars):
  G – Em – C – G

Verse (4 bars):
  G – D – Em – C

Chorus (4 bars):
  F - Am - D - G  
```

### Audio Output

* Sections are concatenated into a single MIDI sequence
* Fixed tempo
* Piano instrument
* Block-chord realization

Audio playback remains a **demonstration layer only**.

---

## Design Rationale

v2.5 deliberately models **musical structure**, not narrative emotion.

Section roles are defined by:

* harmonic motion
* cadence behavior
* tonal stability

Emotional contrast emerges **implicitly** through musical function, rather than explicit user directives.

This keeps v2.5:

* musically grounded
* explainable
* tightly scoped

---

## Version Freeze Statement

Version 2.5 is **complete and frozen**.

* Section templates locked
* Constraint rules locked
* Key/mode policy locked
* Orchestration logic locked

All future versions must preserve v2.5 behavior as a valid generation path.

---

## Looking Ahead

Future versions may introduce:

* user-directed emotional arcs per section
* modulation and key transitions
* richer section templates
* melody-aware harmony

These features are explicitly **out of scope** for v2.5.
