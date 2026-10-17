---
description: Validate a transcript before TTS generation
argument-hint: "<path-to-transcript-md>"
---

If no transcript path is provided, respond with exactly one line:

Usage: /validate-transcript <path-to-transcript-md>

Otherwise, validate the transcript at `${1}` before TTS generation. The transcript may have been generated in the current chat, generated in another directory, or generated in a different session and later moved into this project.

Read and follow the format defined in `transcripts/expected-transcript-format.md`. Read the transcript without modifying it.

First, run the deterministic format validator from the project root:

```bash
python .pi/skills/podcast-transcript-builder/scripts/validate_format.py "${1}"
```

Treat a non-zero exit status as a format failure and report the validator’s errors. Do not duplicate checks that the script already performs. Then perform the remaining dynamic/content checks:
- Dialogue contains spoken text only and no Markdown formatting.
- Speaker labels are consistent and appropriate for the transcript; do not assume they must be `Coach:` or `Engineer:`.
- Identify issues that could cause TTS or chunking problems.
- Check that humor markers, if present, are standalone and placed immediately before the humor bit.

Report:
- Overall pass/fail status, combining the script result and dynamic checks.
- Specific errors with line or section references.
- Warnings for likely TTS or chunking issues.
- Concrete suggested corrections.

Do not edit the transcript or any other file automatically.

End the summary exactly with:

apply the above suggested edits?
