---
description: Validate a transcript before TTS generation
argument-hint: "<path-to-transcript-md>"
---

If no transcript path is provided, respond with exactly one line:

Usage: /validate-transcript <path-to-transcript-md>

Otherwise, validate the transcript at `${1}` before TTS generation. The transcript may have been generated in the current chat, generated in another directory, or generated in a different session and later moved into this project.

Read and follow the format defined in `transcripts/expected-transcript-format.md`. Read the transcript without modifying it.

Check:
- An optional title is allowed.
- Every dialogue line starts with exactly `Coach:` or `Engineer:`.
- Dialogue contains spoken text only.
- Dialogue contains no Markdown formatting.
- Each speaker turn is one line or one paragraph.
- Pauses use bracketed timing cues such as `[pause 3 seconds]`.
- Identify issues that could cause TTS or chunking problems.

Report:
- Overall pass/fail status.
- Specific errors with line or section references.
- Warnings for likely TTS or chunking issues.
- Concrete suggested corrections.

Do not edit the transcript or any other file automatically.

End the summary exactly with:

apply the above suggested edits?
