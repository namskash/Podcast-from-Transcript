# Gemini TTS: Making Generated Podcasts Feel More Natural

## Context

Reviewed:

- `.agents/prompts/generate-transcript.md`
- `.agents/skills/podcast-transcript-builder/SKILL.md`
- `transcripts/linux-file-descriptors.md`
- `src/podcast_from_transcript/cli.py`

The current transcript is clear and technically strong, but it is highly symmetrical: nearly every turn is a complete question/answer pair, with little interruption, reaction, hesitation, or conversational drift. The main fix should happen during transcript generation, not through random TTS settings.

## What Gemini TTS accepts

For the current Gemini TTS API/SDK used by this project:

- `response_modalities=["AUDIO"]`
- `speech_config.voice_config.prebuilt_voice_config.voice_name`
- `speech_config.language_code`
- `speech_config.multi_speaker_voice_config.speaker_voice_configs[]`
- Per text part, `speech_metadata.speaker`
- Per text part, `speech_metadata.style`
- Natural-language style instructions for delivery, such as conversational, warm, relaxed, thoughtful, or lightly hesitant
- Inline transcript cues for pauses and vocal events. Current Google guidance uses cues such as `<short pause>`, `<long pause>`, `<breath>`, `<sigh>`, and `<chuckle>`; punctuation such as `...`, commas, and em dashes also affects delivery.

The current Python SDK types confirm that `SpeechConfig` exposes voice/language/multi-speaker settings and that `Part` exposes `SpeechMetadata(speaker, style)`.

Gemini TTS does **not** expose the usual numeric `speakingRate` or `pitch` controls in this request path. Use style instructions and transcript wording instead. Numeric `speakingRate` and `pitch` belong to Google Cloud Text-to-Speech's separate API, not Gemini `generate_content`.

## Recommended transcript-generation changes

**Accepted suggestions:** 1–4  
**Ignored for now:** 5 and everything below this point

1. **Add conversational structure, not just information structure.**
   - Use fewer perfectly alternating Q/A turns.
   - Let one speaker react before explaining: “Right,” “Exactly,” “Wait—why does that happen?”
   - Add occasional follow-up questions and clarifications.
   - Allow a speaker to answer briefly, then expand after a follow-up.
   - Vary turn length: short reactions mixed with longer explanations.
   - Include occasional references to what was just said: “That last part is important.”

2. **Add a small amount of natural imperfection.**
   - Use contractions and spoken phrasing.
   - Use sentence fragments occasionally.
   - Add pauses at topic transitions or before an important explanation.
   - Avoid inserting a pause after every turn; that will sound mechanical.

3. **Make personalities affect interaction.**
   The current “expert/newbie” pairing mostly creates predictable questions. Give each speaker conversational habits, for example:
   - one speaker interrupts gently or asks for a concrete example;
   - the other notices confusion and rephrases without sounding like a textbook;
   - either speaker occasionally says “That’s a good question” or corrects themselves.

4. **Reduce exposition blocks.**
   Break long expert answers into smaller turns. Have the other speaker summarize, challenge, or ask for an example before the next concept. This will improve both pacing and perceived spontaneity.

5. **[IGNORED] Use explicit pauses sparingly.**
   The skill already supports `[pause N seconds]`, and the current pipeline converts these to Gemini-style `<pause N seconds>` tags. Keep these for meaningful beats—roughly one every few topic transitions—not as punctuation between every line.

## [IGNORED] Optional filler-word treatment

Filler words should be an optional, low-frequency style choice rather than a default. Add only where a human speaker would plausibly hesitate:

- “Hmm, let me think about that.”
- “Um, the short version is...”
- “Right—so...”
- “Well, actually...”
- “Oh, yeah, that’s the tricky part.”

Use them more often for one speaker than the other, and avoid repeated “um”/“uh” patterns. A few meaningful hesitations are convincing; evenly distributed filler words sound synthetic.

The current format validator permits ordinary spoken filler text. It does not currently define dedicated filler or backchannel syntax. Do not add a new syntax unless the parser and validator are updated together.

## [IGNORED] Recommended TTS style defaults

Replace the generic default style `natural podcast narration` with a more specific but short instruction, for example:

```text
casual, warm, conversational podcast dialogue; relaxed pacing; natural pauses; responsive and lightly expressive; do not sound like an audiobook or newsreader
```

For multi-speaker turns, keep the shared style short and let the transcript carry the personality. If desired, use per-speaker styles, such as:

- Coach: curious, encouraging, animated, conversational
- Engineer: calm, precise, thoughtful, conversational

Avoid very long style prompts or conflicting instructions. Test the transcript with a minimal style first, then add only the delivery attribute that is missing.

## [IGNORED] Suggested prompt/skill changes

Add a generation requirement along these lines:

> Write an informative but genuinely conversational exchange. Vary turn length and rhythm. Include occasional reactions, follow-up questions, clarifications, brief backchannels, and topic-transition pauses. Do not make every turn a polished question followed by a complete answer. Use filler words only when natural and only if the optional “conversational disfluencies” setting is enabled.

Add an optional configuration choice:

- `conversational_disfluencies`: none (default), light

“Light” should permit a few fillers, self-corrections, and backchannels; it should not add them mechanically.

## [IGNORED] Suggested CLI/style changes

The current implementation already supports the important Gemini controls:

- multi-speaker voice mapping;
- `SpeechMetadata(speaker, style)`;
- pause conversion from `[pause ...]` to `<pause ...>`;
- a configurable `--style` argument.

The lowest-risk implementation change is therefore just improving the default `--style` string and documenting style examples. The larger quality improvement should come from changing transcript-generation guidance and adding more varied dialogue patterns.

Do not add `temperature`, `top_p`, or random generation settings specifically to create vocal naturalness. Those are general generation controls, not reliable speech-rate or prosody controls, and may reduce consistency.

## Sources

- Google AI for Developers, “Text-to-speech generation (TTS)”: https://ai.google.dev/gemini-api/docs/speech-generation
- Google Cloud, “Gemini TTS prompting guide”: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/text-to-speech/prompting-guide
- Google Cloud, “Gemini-TTS”: https://docs.cloud.google.com/text-to-speech/docs/gemini-tts
- Google Cloud, “AudioConfig” (separate Cloud TTS API): https://docs.cloud.google.com/text-to-speech/docs/reference/rest/v1/AudioConfig

## [IGNORED] Bottom line

Prioritize less predictable dialogue: reactions, follow-ups, varied turn lengths, occasional rephrasing, and purposeful pauses. Use a concise conversational style prompt to guide delivery. Treat filler words as an opt-in light-touch feature, not the primary solution.
