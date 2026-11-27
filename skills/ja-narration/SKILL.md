---
name: ja-narration
description: Rules for Japanese AI narration (ElevenLabs eleven_v4): how to write natural spoken Japanese for a product demo, how to send English terms, brand/term readings (4D, v21, Gemma), cadence pitfalls such as "4Dの", and the text tricks that fix clipped first syllables. Use together with localize-screen-demo whenever the target language is Japanese.
---

# Japanese narration

Read `docs/ja/narration-ja.md` and `prompts/voice-design-ja.txt` in the `elevenlabs-4d` repository.

Essentials:

- Re-tell in spoken です・ます Japanese; about 5 characters per second per scene at most.
- English terms are sent as plain English, except the approved readings: `4D` → `ふぉおでぃい`, `4D v21` → `ふぉおでぃい ぶいにじゅういち`, `Gemma` → `じぇま`. Replace `_` in method names with a space.
- Keep "4D" at the start of a compound (`4Dコード`, `4Dメソッド`); avoid `4Dの…` and `4D自身`. Test cadence in context with two seeds.
- Avoid long-vowel katakana transliterations of English words.
- If a clip's first sound is clipped, prefix the text with `……`; trim the trailing silence and blip.
- Use Voice Design, not pre-made voices, for a natural Japanese accent.
