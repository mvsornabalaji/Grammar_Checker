# AI Grammar Checker

A full-stack grammar-checking web app: **Flask** backend + a rule-based Python
grammar engine, with a modern, responsive **HTML/CSS/JavaScript** frontend
that talks to the backend via the Fetch API (no page reloads).

## Project Structure

```
grammar_checker/
│
├── app.py                 # Flask app & routes (pages + API)
├── config.py               # App configuration (limits, secret key, debug)
├── requirements.txt
├── README.md
├── grammar/
│   ├── __init__.py
│   └── checker.py          # GrammarChecker engine (rule-based, modular)
├── templates/
│   ├── index.html           # Landing page
│   └── checker.html         # Grammar checker tool page
└── static/
    ├── css/
    │   └── style.css        # All styling (design tokens, dark/light mode)
    └── js/
        └── script.js        # Fetch API calls, counters, copy/download, UI
```

## Features

- Landing page with feature highlights and "How It Works" section
- Grammar checker page with a large editor, live word/character counters
- **Check Grammar**, **Clear**, **Copy Corrected Text**, and **Download .txt** buttons
- Detects: subject–verb agreement, articles (a/an), basic verb-tense agreement,
  common prepositions, singular/plural after numbers, common misspellings,
  double spaces, missing/extra spacing around punctuation, and sentence
  capitalization
- Results show original text, corrected text, and a list of mistakes with
  explanations, plus live statistics (words, characters, sentences, mistakes found)
- Dark / light mode toggle (persisted in the browser)
- Input validation, max length limits, and safe (non-executable) rendering
  of all user-provided text

## How the Grammar Engine Works

`grammar/checker.py` defines `GrammarChecker`, a small rule-based pipeline:

1. Normalize whitespace/punctuation (double spaces, spacing around punctuation)
2. Capitalize the start of each sentence
3. Apply an ordered list of `Rule` objects (regex pattern + replacement +
   explanation) covering pronouns, subject–verb agreement, articles,
   prepositions, plurals, and common misspellings
4. Compute writing statistics

The engine is intentionally modular: `GrammarChecker.check(text)` is the only
method the rest of the app depends on. You can later swap the internals for
a call to an AI/API-based grammar model (e.g. an LLM or a service like
LanguageTool) without changing `app.py` or the frontend, as long as the new
implementation returns the same dictionary shape:

```python
{
  "original_text": "...",
  "corrected_text": "...",
  "mistakes": [{"original": "...", "correction": "...", "explanation": "..."}],
  "stats": {"word_count": .., "character_count": .., "sentence_count": .., "mistakes_found": ..}
}
```

**Note:** as a lightweight rule-based system (rather than a full NLP/AI
model), it covers common, well-defined error patterns rather than every
possible grammatical mistake or complex sentence-structure issue.

## API

### `POST /api/check-grammar`

Request:
```json
{ "text": "I has a car." }
```

Response (200):
```json
{
  "original_text": "I has a car.",
  "corrected_text": "I have a car.",
  "mistakes": [
    { "original": "I has", "correction": "I have", "explanation": "Use 'have' with the subject 'I'." }
  ],
  "stats": { "word_count": 4, "character_count": 13, "sentence_count": 1, "mistakes_found": 1 }
}
```

Error responses (400): empty text, text over 5000 characters, missing/invalid
`text` field, or a non-JSON request body.

### `GET /api/health`
Returns `{ "status": "ok" }` — useful for uptime checks.

## Installation (Windows, VS Code)

1. Open the `grammar_checker` folder in VS Code (**File → Open Folder...**).
2. Open a terminal in VS Code (**Terminal → New Terminal**) — it should default
   to PowerShell or Command Prompt.
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate it:
   ```
   venv\Scripts\activate
   ```
   You should see `(venv)` appear at the start of your terminal prompt.
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Run the app:
   ```
   python app.py
   ```
7. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```

To stop the server, press `Ctrl + C` in the terminal. To deactivate the
virtual environment later, run `deactivate`.

## Testing

You can test manually in the browser, or test the API directly.

### Manual test cases (paste into the editor and click "Check Grammar")

| Input | Expected corrected output |
|---|---|
| `He go to school every day.` | `He goes to school every day.` |
| `I are a student.` | `I am a student.` |
| `She have two books.` | `She has two books.` |
| `i has a car` | `I have a car` |
| `This is a correct sentence.` | `This is a correct sentence.` (no mistakes) |
| `` (empty input) | Error: "Please enter some text before checking grammar." |
| A very long text (> 5000 characters) | Error: text exceeds maximum length |
| `teh  book is definately good.` | `The book is definitely good.` (spelling + spacing fixed) |

### Testing the API with curl (after starting the server)

```
curl -X POST http://127.0.0.1:5000/api/check-grammar ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"She have two books.\"}"
```

### API failure handling
- Stop the Flask server, then click "Check Grammar" in the browser — the
  frontend will show a clear error alert ("Unable to reach the server...")
  instead of failing silently.
- Sending a request without a `text` field, or with `text` as a non-string,
  returns a `400` response with a descriptive `error` message.

## Security Notes

- Input length is capped (`Config.MAX_TEXT_LENGTH`, default 5000 characters)
  and Flask's `MAX_CONTENT_LENGTH` further caps the raw request body size.
- All user text is inserted into the DOM using `textContent` (never
  `innerHTML`), so it is never executed as HTML/JavaScript.
- The backend validates that the request is JSON and that `text` is present
  and is a string before processing it.
- No CORS headers are enabled by default since the frontend is served by the
  same Flask app; add `flask-cors` only if you plan to call the API from a
  different origin.
