# TypingMind Plugin Guide

- A practical, skimmable guide to building TypingMind plugins—based on the working examples in this repo.
- Read Developer Documentation: https://www.typingmind.com/plugins-docs
- Demo of the document stats plugin:
  TypingMind Chat: https://cloud.typingmind.com/share/17366e6d-a2de-45b0-8007-0349dffb3f4c


## Quick checklist

- Define plugin spec
  - id, uuid, title, emoji
  - openaiSpec: name, description, JSON schema
  - outputType: cards | respond_to_ai | render_html
  - implementationType: javascript
  - permissions (e.g., read_last_user_message) if needed
  - userSettings with sensible defaults
- Implement code function
  - async function name(params, userSettings, authorizedResources)
  - name MUST match openaiSpec.name
  - No network calls unless allowed; keep sandbox-safe
- Choose distribution path
  - GitHub folder: plugin.json + implementation.js (+ README)
  - JSON editor: single-file bundle with code inline
    - In TypingMind app, go to Plugins > Create Plugin > JSON Editor. Then copy/paste the entire plugin.json file.
- Test import and preview
  - Verify name match, return shape for outputType, and permissions prompts
- Iterate
  - Add toggles (userSettings), optional params, and performance fallbacks

## Core concepts

- openaiSpec: Defines a tool/function the AI can call.
  - name: must match your exported JS function name exactly.
  - parameters: JSON schema for params (type, properties, required, descriptions).
  - description: clear, action-oriented description used by the AI.
- outputType: Controls how TypingMind renders/uses your function output.
  - cards: Return `{ cards: [...] }` for direct UI rendering.
  - respond_to_ai: Return any JSON object; the AI uses it to compose a message.
  - render_html: Return HTML (and inline JS/CSS) to render a view.
- implementationType: javascript (runs in a sandboxed environment).
- permissions: Request runtime data access (e.g., `read_last_user_message`).
- userSettings: Per-plugin configuration UI (number/enum/string/password), available to your code.

## Output types (with return shape)

- cards
  - Return: `{ cards: [{ type: 'text', text: '...' }, ...] }`
  - Use for: Deterministic readouts you want shown as-is.
  - Example: `examples/typingmind_plugin_examples/document_stats/` (cards variant)
- respond_to_ai
  - Return: Arbitrary JSON (e.g., `{ stats, meta, suggestions, ... }`).
  - The AI reads this object and writes the final message (Markdown by default).
  - Example: `examples/typingmind_plugin_examples/tarot_reader/`, plus our `document_stats_ai` variant
- render_html
  - Return: HTML string (simple inline JS/CSS). No external scripts unless allowed by the plugin.
  - Use for: Rich visualizations/controls the cards format can’t express.
  - Example: `examples/typingmind_plugin_examples/mindmap_maker/`

## Minimal plugin anatomy

- Folder import (GitHub):
  - `plugin.json` (spec) and `implementation.js` (code), optional `README.md`.
- JSON editor import:
  - Single JSON with a `code` field containing the function body as a string.
- Function signature:
  - `async function <openaiSpec.name>(params, userSettings, authorizedResources) { ... }`
  - Use `authorizedResources.lastUserMessage` if you requested `read_last_user_message`.

## Our process outline (what worked)

1) Explore examples and patterns
   - Looked at `book_search`, `image_editor`, `mindmap_maker`, `tarot_reader` to copy proven shapes.
2) Implement a minimal working plugin
   - Built `document_stats` (cards) for fast local stats. No network calls.
3) Validate vs docs and tighten schema
   - Ensured openaiSpec.name matches code function name.
   - Added optional params and userSettings toggles.
4) Add improvements and toggles
   - Avg metrics, readability toggle, include_json option, performance.now fallback.
5) Distribution setup
   - GitHub importer requires `plugin.json` specifically.
   - For JSON editor, created a single-file bundle with inline `code`.
6) Resolve common errors
   - “Code implementation is required”: add `code` (JSON editor) or `implementation.js` (folder).
   - “Function name is not defined”: ensure function name matches `openaiSpec.name` exactly.
7) Offer an AI-insights variant
   - Added `document_stats_ai` (respond_to_ai) so the AI can summarize and format in Markdown/HTML.

## Tips and best practices

- Name matching is strict
  - openaiSpec.name must equal the JS function name you export.
- Choose outputType early
  - cards for fixed UI output, respond_to_ai for AI narratives, render_html for custom visuals.
- Keep code sandbox-safe
  - Avoid window globals assumptions; handle missing APIs with fallbacks.
- Be explicit in your JSON schema
  - Provide clear param descriptions to guide the AI.
- Lean on userSettings
  - Allow tuning (e.g., words_per_page, toggles) instead of hardcoding thresholds.
- Handle empty/edge input
  - Return a friendly message or empty result instead of throwing.
- Performance
  - Use `performance.now()` when available, fallback to `Date.now()`.
- Determinism vs. creativity
  - Use cards for predictable outputs; use respond_to_ai to let the AI add insights.

## Things to avoid (pitfalls)

- Mismatched names
  - If `openaiSpec.name` != function name → runtime error.
- Wrong return shape for outputType
  - cards must return `{ cards: [...] }`; render_html must return HTML; respond_to_ai returns data.
- Missing plugin.json for GitHub import
  - Importer expects `plugin.json` (not a differently named spec) in the folder root.
- JSON string escaping (JSON editor bundles)
  - Escape backslashes in regex (e.g., `\\b`), newlines (`\\n`), and `\r` sequences.
- Assuming lastUserMessage exists
  - Request `read_last_user_message` and still guard for null.
- Heavy/blocked operations
  - Long loops or large DOM work can stall the UI. Keep it light.

## Distribution paths

### GitHub folder import
  - Public repo path pointing to a folder containing `plugin.json` + code files.
    - filenames must be exactly "implementation.js" and "plugin.json"
  - Good for versioning and sharing.
  - https://docs.typingmind.com/plugins/share-import-plugins#:~:text=Share%20via%20GitHub
### JSON editor import
  - One file containing the entire spec with `code` inline—quick to copy/paste.
  - Watch out for proper escaping in the `code` string.
### Default import format
```
{
  "uuid": "771ed278-41fd-44f8-803d-4260fc7b4c1f",
  "id": "new_plugin_id_9282152",
  "title": "New Plugin",
  "overviewMarkdown": "## New Plugin\n\nDescribe your plugin here",
  "openaiSpec": {
    "name": "new_plugin_id_9282152",
    "description": "Description for the function",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Description of the first parameter"
        }
      },
      "required": [
        "param1"
      ]
    }
  },
  "userSettings": [
    {
      "name": "variableName1",
      "label": "Variable Name 1",
      "description": "This value will be provided by the user and passed to the plugin function when called",
      "required": true
    },
    {
      "name": "varibaleName2",
      "label": "Variable Name 2",
      "description": "This value will be provided by the user and passed to the plugin function when called",
      "type": "password",
      "required": true
    }
  ],
  "code": "# Your JS code here",
  "syncedAt": null
}
```


## Troubleshooting quick hits

- Cannot preview plugin: Code implementation is required
  - Add `implementation.js` (folder) or a `code` field (JSON editor).
- Function name is not defined in your code
  - Ensure the function name exactly matches `openaiSpec.name`.
- GitHub import failed
  - Ensure the folder has `plugin.json` (not just a renamed spec).
- Cards rendered as plain text only
  - Confirm card objects have `type: 'text'` and `text` string.
- HTML not rendering as expected
  - Keep it simple; avoid external script tags. Inline CSS/JS only.

## Testing and validation

- Smoke test with tiny inputs (and empty string) to ensure no throws.
- Try both param-provided text and last_user_message fallback.
- Toggle userSettings to verify logic paths.
- Validate outputType return shapes:
  - cards → see rendered card(s)
  - respond_to_ai → the AI writes a summary using your returned JSON
  - render_html → HTML shows as intended in the sandbox

## Examples in this repo

- Cards: `examples/typingmind_plugin_examples/document_stats/`
- Respond to AI: `examples/typingmind_plugin_examples/tarot_reader/`, `document_stats_ai` variant
- Render HTML: `examples/typingmind_plugin_examples/mindmap_maker/`

## Next steps

- Decide which outputType suits your UX.
- Start from a minimal spec and function; import via JSON editor for rapid iteration.
- Add userSettings and optional params.
- When stable, publish via a GitHub folder with `plugin.json` and a short README.
