# AI Pipeline

## Model

CoralAI uses **Google Gemini Vision** (`gemini-2.0-flash` by default, configurable via `GEMINI_MODEL`) for multimodal image classification. It was chosen over training a custom CNN because:

- Zero training data required — critical for a 24-hour hackathon build.
- Strong out-of-the-box performance on general marine/underwater imagery.
- Native structured-output support (forced JSON) simplifies backend parsing.

## The Prompt

The exact prompt sent with every image (hardcoded in `src/backend/app/services/gemini_service.py`, `GEMINI_PROMPT`):

```
You are an expert marine biologist specializing in coral reef health.
Analyze the uploaded underwater coral image.
Respond ONLY in valid JSON.
{
"classification": "",
"severity": "",
"confidence": 0,
"possible_cause": "",
"recommendation": ""
}
Classification must be one of:
Healthy
Partially Bleached
Severely Bleached
Dead Coral
Unknown
Estimate confidence from 0-100.
Do not include markdown.
```

This prompt is deliberately strict — it fixes the response schema, constrains `classification` to a closed enum, and forbids markdown fencing, so the backend can parse the response deterministically.

## Request Flow

```
image bytes (resized, ≤1600px) ──┐
                                   ├──▶ genai.GenerativeModel(GEMINI_MODEL)
GEMINI_PROMPT (hardcoded)  ───────┘         │
                                             ▼
                                   response.text (raw string)
                                             │
                                             ▼
                          _extract_json()  — strips markdown fences,
                                              regex-extracts the {...} block
                                             │
                                             ▼
                        _validate_result() — coerces confidence to [0,100],
                                              rejects unknown classification
                                              values by falling back to
                                              "Unknown"
                                             │
                                             ▼
                              validated dict returned to api/analyze.py
```

## Defensive Parsing

Even with a strict prompt, LLM output can't be trusted as valid JSON unconditionally. `gemini_service.py` defends against:

- **Markdown-wrapped JSON** (` ```json ... ``` `) — stripped via regex before parsing.
- **Extra prose around the JSON block** — the JSON object is extracted with a greedy `\{.*\}` regex match rather than assuming the entire response is JSON.
- **Invalid/hallucinated classification values** — anything outside the fixed 5-value enum is coerced to `"Unknown"` rather than propagated, so downstream risk scoring and UI badges never see an unexpected value.
- **Non-numeric or out-of-range confidence** — coerced to a float and clamped to `[0, 100]`.
- **API/network failures or missing `GEMINI_API_KEY`** — the whole call is wrapped in a try/except that returns a safe fallback (`classification: "Unknown"`) instead of raising, so one bad image never breaks the upload pipeline for the user.

## Coral Risk Engine

The Risk Engine (`_compute_risk` in `src/backend/app/api/analyze.py`) is intentionally simple, per the hackathon scope — it's a transparent, explainable scoring function rather than a second ML model:

1. Start from a base score per classification:
   `Healthy=0, Partially Bleached=40, Severely Bleached=75, Dead Coral=100, Unknown=20`
2. Add a temperature penalty using sea surface (or air) temperature:
   - `+10` if temperature ≥ `RISK_TEMP_WARNING_C` (default 29.5°C)
   - `+20` if temperature ≥ `RISK_TEMP_CRITICAL_C` (default 30.5°C)
3. Clamp to `[0, 100]` and bucket into a label:
   `<25 Low`, `<50 Moderate`, `<75 High`, `≥75 Critical`

This gives a single, explainable number that combines what the AI *saw* with what the environment *predicts*, without requiring a second trained model.

## Future Improvements

- Fine-tune or few-shot the prompt with example images per classification to improve consistency.
- Add a confidence-based human-review queue for low-confidence (<50%) classifications.
- Track classification drift over time per reef site to detect trends the single-image model can't see.
