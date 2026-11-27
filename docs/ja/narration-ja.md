# Japanese narration (language-specific)

Applies to ElevenLabs voice-over in Japanese. General rules are in `docs/global/`.

## Writing the script

- **Re-tell, do not translate.** A transcript of a live demo is wooden in Japanese. Keep scene order, facts and numbers; use です・ます, short sentences, questions to the viewer ("さあ、AIはどうするでしょうか"), and light live commentary ("当たりです"). Mark added flourishes so the owner can veto them.
- Keep product/UI/method names exactly as on screen (`get_current_user`, `weatherAdvisor`); the on-screen UI stays English, so add caption (テロップ) suggestions.
- Do not add claims the speaker did not make; keep the speaker's own claims attributed ("…という声があります" style only if the owner agrees).
- Budget: about **5 characters/second** (excluding 、。) is the ceiling for a scene. Real ElevenLabs output averaged ≈ 5.6 characters per second of audio including pauses; ElevenLabs puts ≈ 1 s between sentences.

## Pronunciation rules learned

1. **Send English terms as plain English** (AI, LLM, MCP, API, OpenAI, Claude, Ask Me Anything, Event Pulse, VIP, method names). Katakana/hiragana transliterations with long-vowel marks (`エーアイ`) were unstable, and spelled-out versions such as `あすく みい えにしんぐ` were read as `いえにしんぐ`.
2. **Exceptions** (approved for the 4D project):
   - `4D` → `ふぉおでぃい` (brand; never compromise; see below)
   - `4D v21` → `ふぉおでぃい ぶいにじゅういち`; `v21` alone → `ぶいにじゅういち`
   - `Gemma` → `じぇま` (the model said じぇんま)
3. **Method names with underscores** are read badly; replace `_` with a space (`get current user`). camelCase names (`weatherAdvisor`) were fine.
4. **Brand "4D" cadence.** The wanted accent is flat-high after a low first mora (low-high-high-high). The model gets it when "4D" starts a compound (`4Dアプリ`, `4Dコード`, `4Dメソッド`, `4D v21…`) and gets it wrong before の (`4Dのコード`) or in `4D自身`. Spelling variants (カタカナ, raw `4D`, `ふぉーでぃー`, comma before, small `ぃ`, space after `ふぉ`) did not fix it: **the grammatical context decides**. Rewrite the sentence (`4Dコード`, `4Dメソッドそのもの`) rather than respelling. Test candidates in context, two seeds each.
5. A sentence that starts with `4D v21には、…` had a bad cadence; moving it mid-sentence after "もう一つ、" and rendering **without** previous/next text fixed it.
6. Scene openings such as `では、…` / `次の…` were not a wording problem: the clip's first syllable was clipped by the service (see `docs/global/02-elevenlabs.md`, prefix `……`). Rewording them was unnecessary.
7. Numbers and counters (`5社`, `10件`, `12月1日`) were read correctly.

## Process tips

- Pronunciation questions: render a small batch with letter-coded variants and ask the user to choose; do not guess.
- Use hiragana for forced readings and keep them out of the draft shown to the owner (the draft keeps `4D`; the TTS file applies the table in `tools/make_tts.py`).
- Pitch contour cannot be set directly; there is no accent control in the API. Only text, context and seed influence it.

## Voice

`prompts/voice-design-ja.txt`: calm, warm, 35–45, standard Tokyo Japanese, ≈ 5 characters per second, subtle emphasis only on key terms and numbers. Pre-made English voices speak Japanese with an accent; use Voice Design.
