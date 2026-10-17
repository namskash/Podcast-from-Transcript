# Podcast Transcript Prompt Decisions

Date: 2026-10-17

- The prompt starts by collecting the topic and source material.
- Add a second planning step for follow-up questions about the topic and focus areas.
- After topic follow-ups, offer a pit stop with two paths:
  - Go with defaults and proceed directly to transcript generation.
  - Decide each configuration option individually.
- Ask configuration questions one at a time; never present all questions simultaneously.
- If the harness provides a suitable interactive TUI for arrow-key or typed selection, use it.
- If no suitable TUI exists, present the options in the prompt and let the user reply.
- Every custom, non-default selection is staged in a run-specific file under `./tmp/` while questions are being answered.
- After the transcript is successfully saved and validated, persist the staged choices to `./docs/choice-selection-history.json` in one final step.
- Store usage counts under dedicated choice keys, with selected values mapped to the number of times used. For example, `personalities` stores personality descriptions and their counts.
- Persistence searches each dedicated choice key, increments an existing selected value, or creates a new value with count 1.
- Offer previous choices from the history file in future questions, sorted by usage count descending; allow free-text choices where appropriate.
- Do not add a separate Custom questionnaire option; use the questionnaire’s Other option for free-text answers.
- Ask selections for:
  1. Podcast length: short (~5 minutes), standard (~10 minutes, default), extended (~20 minutes), or long (~30 minutes).
  2. Number of speakers: 1, 2 (default), or 3.
  3. Speaker names or labels: `Coach` and `Engineer` (default), or use Other for different labels.
  4. Personality description for each speaker, either a previous history choice or Other; default to distinct, natural personalities.
  5. Transcript humor level: none, light (default), playful, or frequent.
  6. References, metaphors, or comparisons: none (default), or choices such as cricket, Linux, badminton, painting, or Rubik’s Cube.
- If one speaker is serious and another humorous, automatically place jokes primarily in the humorous speaker’s dialogue.
- The prompt owns the workflow; the skill remains minimal and format-focused.
- The prompt does not separately instruct the agent to read the format file and the skill; the skill already instructs the agent to read `@transcripts/expected-transcript-format.md`.
- After configuration, draft human-like dialogue shaped by each speaker’s personality.
- Mark humor with standalone `<!-- HUMOR -->` markers.
- Save transcripts only under `./transcripts/<slug>.md`.
- Run `validate_format.py` after drafting.
- Fix validation errors before finishing and report the saved transcript path.
