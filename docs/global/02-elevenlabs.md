# ElevenLabs text-to-speech

## Setup

- Run `npx -y @elevenlabs/cli@latest onboard init` in the project folder: browser sign-in, key stored in `.env` (and `onboard check` / `onboard test` verify it). Never print or paste the key; scripts load `.env` themselves (`tools/_el.py`).
- Use the Python SDK (`pip install elevenlabs`): `client.text_to_speech.convert(voice_id, text=…, model_id="eleven_v4", language_code="ja", …)`.

## What you actually send

- **Plain text only.** The text box reads everything aloud: Markdown headings, code fences, `*`, and tags the model does not support. Generate `tts_txt/S01.txt` per scene and paste/send only that.
- `eleven_v4` (default in the current skill): no SSML, so `<break time="…"/>` is **read aloud**; no `speed` or `style` setting; audio tags like `[whispers]` are supported. Older models (Multilingual v2) accept `<break>` but not audio tags. Pause control with v4 = punctuation and sentence length.
- There is no field for "cadence direction". Delivery is shaped only by the voice, the text, the settings and the surrounding context.

## Voices

- Pre-made voices are English-accented when reading other languages. Use **Voice Design**: `text_to_voice.design(voice_description=…, text=<sample>)` returns 3 previews; `text_to_voice.create(generated_voice_id=…)` saves one to the account. Previews expire, so save the one you pick. See `prompts/voice-design-ja.txt`.
- Re-render an already approved preview with new text by saving it first (that is the only way to hear it again).
- Generate **one clip per scene** with the same voice, model and settings.

## Context and consistency

- `previous_text` / `next_text` smooth the join between scenes but change prosody. In one scene a clean "solo" render (no context) gave the correct cadence for a brand term while the context version did not. Offer both in A/B tests; keep a per-scene override (`EL_NOCTX`).
- `seed` gives reproducible takes; the same text with different seeds can differ in pitch. For cadence tests render at least two seeds.

## Defects to detect and fix

- **Clipped first syllable.** Some clips start already at full level ("では" and "次の" lost their first sound, heard as a loss of audio). Measure the peak of the first 20 ms: more than about −38 dBFS means truncated. Retrying with other seeds mostly failed; **prefixing the text with `……`** gave a clean soft onset every time (`tools/make_narration.py`, `EL_NOLEAD` to opt out).
- **Trailing silence and a stray blip.** Clips end with about 0.9 s of silence plus a 0.1 s click/breath. Cut at last-silence-start + 0.25 s (`tools/trim_narration.py`) before computing scene lengths.
- Add a 40 ms fade-in to each clip in the mix as a safety net.

## Cost note

Voice previews and tests spend credits; ask before large batches. A whole 10-minute narration is a few thousand characters.
