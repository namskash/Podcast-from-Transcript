---
name: podcast-transcript-builder
description: Enforce the project’s podcast transcript format when creating a transcript.
---

# Podcast Transcript Format

Read `@transcripts/expected-transcript-format.md`.

**Speaker characterization:** Use the speaker roles and personalities supplied by the command to make the transcript human-like and personal, with each speaker’s distinct voice evident throughout. If none are supplied, default to two speakers.

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

Save the transcript in `./transcripts/` and run `scripts/validate_format.py <transcript-path>` at the end. Fix any validation errors before finishing.
