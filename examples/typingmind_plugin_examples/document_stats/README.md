## Document Stats TypingMind Plugin

Fast client-side statistics for a block of text. Returns only aggregated metrics (never echoes original text). No network calls.

Metrics:
- Words
- Sentences
- Complex Sentences (heuristic: contains comma, semicolon, or coordinating/subordinating conjunction)
- Paragraphs (blank-line separated)
- Estimated Pages (configurable words/page, default 250)
- Avg Words per Sentence
- Avg Syllables per Word
- Flesch Reading Ease (0–100, optional / skippable)
- Processing time (ms)

Usage:
1. Invoke with optional `text` parameter.
2. If `text` is omitted, analyzes last user message (requires `read_last_user_message` permission).
3. Add `include_json: true` in call params OR set user setting `return_json_card` to Yes for a JSON payload card.
4. Toggle readability calculation with `enable_readability` user setting (skip to save cycles on very large inputs).

User Settings:
- `words_per_page` (number, default 250)
- `enable_readability` (Yes/No, default Yes)
- `return_json_card` (Yes/No) – include a second card with JSON.

Optional Call Parameters:
- `text` (string) – explicit text to analyze
- `include_json` (boolean) – override to force JSON card for this invocation even if setting is No

Return Shape (outputType: `cards`):
```jsonc
{
  "cards": [
    { "type": "text", "text": "Document Statistics..." },
    { "type": "text", "text": "Raw JSON: {...}" } // optional
  ]
}
```

No external API calls. All computation happens instantly in JavaScript.

Notes:
- Readability uses a heuristic syllable counter and may fluctuate on very short samples (<3 sentences).
- Empty or whitespace-only input returns zeros.
- Complex sentence heuristic is intentionally simple; it’s a proxy for coordination/subordination, not full parsing.
- Pages are a rough estimate only.

Sample Prompt for AI:
"Analyze the following text with the Document Stats plugin and include JSON:\n\n<PASTE TEXT HERE>"

Error / No Text Behavior:
- If neither `text` nor last user message text is available, returns a single explanatory card.
