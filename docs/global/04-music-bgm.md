# Background music (Suno)

## Licensing: check the plan before generating

- As we understand Suno's terms, tracks made on the **free plan are owned by Suno and limited to non-commercial use**, and upgrading later does not change that for tracks already made; tracks made while on a **paid plan** are owned by the subscriber with commercial use. Terms change: read them on the dates you generate.
- For a product/marketing demo, subscribe **before** generating the tracks you will ship. Do not redistribute Suno tracks (for example in a public repository) unless the plan allows it.
- Same idea for ElevenLabs: commercial use of generated speech depends on the plan used.

## Prompting

- Use Custom mode with Instrumental on. Put an **Exclude** list (vocals, EDM drop, trap hi-hats, harsh synth, repetitive loop…).
- Style prompt (under 1000 characters): genre/instrumentation, mood, **BPM and key**, arc ("builds to a peak a third of the way through, then settles"), and "leaves space for narration". Structure tags in the lyrics box (`[Intro: …] [Build: …] [Outro: …]`) steer the arc.
- A 14-minute video does not fit one track. Split by scene groups into 2–4 tracks of ~3 min and give each a role (curious opening → build at the demo's high point → focused explanation → warm finale). Keep one key and tempo family so joins work. See `prompts/suno-styles.md`.
- Suno tracks come out longer than asked and end with a fade; that is useful (see below).

## Joining the tracks (`tools/plan_bgm.py`)

- Detect tempo and bar lines with `librosa`. **Give it a tempo hint** (the BPM you asked Suno for, max ≈ 1.12×): unconstrained tracking returned 4/3 of the true tempo and a wrong 3-beat "bar".
- Cut each track on a **bar start**, preferring a quiet bar (phrase break) near the target scene boundary; cross-fade over one bar (`acrossfade=d=<bar> c1=qsin c2=qsin`).
- **End naturally**: use the *end* of the last track so its own cadence and fade-out land on the video's end; skip its intro if needed. Add a short (3 s) extra fade only as safety.
- Fade the first track in over ~1.5 s.

## Level

- Constant music level, no ducking (the user preferred this). A level of about −29 dBFS under narration at about −20 dBFS was approved: `volume=0.3` on Suno tracks that measure about −18 dBFS RMS.
- Check the stem separately (render music alone) when something sounds wrong; compare mix = narration + music to find real dropouts.
