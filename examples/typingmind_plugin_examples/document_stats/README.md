## Document Stats TypingMind Plugin

Fast client-side statistics for a block of text. Returns only aggregated metrics (never echoes original text):

Metrics:
- Words
- Sentences
- Complex Sentences (heuristic: contains comma, semicolon, or coordinating/subordinating conjunction)
- Paragraphs (blank-line separated)
- Estimated Pages (configurable words/page, default 250)
- Flesch Reading Ease (0–100)
- Processing time (ms)

Usage:
1. Run the plugin with optional `text` parameter.
2. If `text` not supplied, it analyzes the last user message (permission required).
3. Optionally enable a raw JSON card via user setting.

User Settings:
- `words_per_page` (number, default 250)
- `return_json_card` (Yes/No) – include a second card with JSON.

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
- Readability is approximate (heuristic syllable counter).
- Empty or whitespace-only input returns zeros.
