---
description: Create a podcast transcript from a topic and source material
argument-hint: "[topic or source]"
---

Use the `podcast-transcript-builder` skill for transcript-format and speaker-characterization requirements.

## Workflow

1. **Topic and source material**
   - Use the user’s supplied request `${@}` as the starting point.
   - If no topic or source material is supplied, ask for it.
   - Accept pasted material, file paths, URLs, or a topic to research.
   - Read supplied local files and use provided source material as the factual boundary.

2. **Follow-ups and focus areas**
   - Ask one concise follow-up question about the topic’s goals, focus areas, exclusions, or must-cover points.
   - Ask only what is needed; allow the user to say “no preference.”

3. **Configuration pit stop**
   At the start of this step, run:

   ```bash
   python .agents/scripts/choice_history.py begin
   ```

   Use the exact returned temporary stage-file path in every subsequent staging and persistence command. Call this path `STAGE_FILE` in the workflow below. Stage custom selections there; do not update the persistent history during the questions.

   Present two options:
   - **Go with defaults** — apply all defaults and proceed directly to transcript generation.
   - **Decide each one** — ask the configuration questions below, one at a time.

   If the `questionnaire` tool is available, use it for selection questions. Use exactly one question per tool call. If it is unavailable, present one question and wait for the user’s reply. Never show all configuration questions at once.

   For each question, first run:

   ```bash
   python .agents/scripts/choice_history.py list <choice-key>
   ```

   Offer the returned choices sorted by usage count, along with the default. Do not add a separate Custom option; when using the questionnaire, its Other option handles free-text answers. Do not stage a default selection. Whenever the user selects a non-default option, stage it immediately:

   ```bash
   python .agents/scripts/choice_history.py stage <STAGE_FILE> <choice-key> "<selected value>"
   ```

   Use these questions and defaults:

   1. **How long should the podcast be?**
      - Options: short (about 2–3 minutes), standard (about 5 minutes, **default**), extended (about 10 minutes), or long (about 20 minutes)
      - Choice key: `podcast_length`

   2. **How many speakers?**
      - Options: 1, 2 (**default**), or 3
      - Choice key: `speaker_count`

   3. **What are the speakers’ names or labels?**
      - Options: `Coach` and `Engineer` (**default**); use Other for different labels
      - Choice key: `speaker_labels`

   4. **What is each speaker’s personality?** Ask separately for each speaker.
      - Default: distinct, natural personalities suited to the topic (a curious, encouraging Coach and a precise, analytical Engineer)
      - Options: the default or a history choice; use Other for a new description
      - Choice key: `personalities`

   5. **What is the transcript’s humor level?**
      - Options: none, light (**default**), playful, or frequent
      - Choice key: `humour_level`
      - If one speaker is serious and another humorous, put jokes primarily in the humorous speaker’s dialogue.

   6. **What references, metaphors, or comparisons should be used?**
      - Use a multi-select question when the questionnaire supports it.
      - Options: none (**default**), or individual references such as cricket, Linux, badminton, painting, or Rubik’s Cube.
      - If multiple references are selected, stage each reference as a separate value under `references`; never stage the combined selection as one value.
      - Choice key: `references`

4. **Draft**
   - Build a clear episode arc around the topic and focus areas.
   - Draft human-like dialogue shaped by each speaker’s personality, with each voice distinct throughout.
   - Apply the selected humor level and references.
   - Mark every humor bit with a standalone `<!-- HUMOR -->` line.

5. **Save and validate**
   - Save only under `./transcripts/<slug>.md`.
   - Do not overwrite an existing transcript without confirmation.
   - Run:

   ```bash
   python .agents/skills/podcast-transcript-builder/scripts/validate_format.py ./transcripts/<slug>.md
   ```

   - Fix every validation error and run the validator again.
   - Persist the staged custom choices only after the transcript has been successfully saved and validated:

   ```bash
   python .agents/scripts/choice_history.py persist <STAGE_FILE>
   ```

   - Report the final saved transcript path and any important assumptions.
