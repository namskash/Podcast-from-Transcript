---
name: podcast-transcript-builder
description: Use only when creating a new podcast transcript; do not use for validating or processing an existing transcript.
---

# Podcast Transcript Format

**Scope:** Use this skill only while creating a new transcript. Do not invoke it for reading, validating, converting, or generating audio from an existing transcript.

Read `@transcripts/expected-transcript-format.md`.

**Speaker characterization:** Use the speaker roles and personalities supplied by the command to make the transcript human-like and personal, with each speaker’s distinct voice evident throughout. If none are supplied, default to two speakers.

**Conversational structure:** Build an informative but genuinely conversational exchange.

- Do not make every turn a polished question followed by a complete answer.
- Include occasional reactions, acknowledgements, follow-up questions, clarifications, and gentle challenges.
- Let speakers refer back to points made in preceding turns.
- Vary turn length and rhythm, mixing short reactions with longer explanations.
- Let one speaker react briefly before giving a fuller explanation.
- Break long explanations into multiple turns with responses between them.
- Use contractions, spoken phrasing, and occasional sentence fragments where natural.
- Allow minor, natural rephrasing or self-correction without adding awkwardness mechanically.
- Use pauses only at meaningful topic transitions.

Do:

```text
Speaker-name: <spoken text>
```

Do not:

```text
"Speaker name": <spoken text>
```

Keep dialogue as spoken text only. Use bracketed pause cues such as `[pause 3 seconds]`.

Mark every humour bit with a standalone `<!-- HUMOR -->` line immediately before it. The marker is not spoken and is removed by the audio pipeline.

Save the transcript in `./transcripts/` and, from the project root, run `.agents/skills/podcast-transcript-builder/scripts/validate_format.py <transcript-path>` at the end. Fix any validation errors before finishing.
