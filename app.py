"""
app.py
------
Entry point for the AI Grammar Checker Flask application.

Routes:
    GET  /                    -> Home / landing page
    GET  /checker              -> Grammar checker page
    POST /api/check-grammar    -> JSON API used by the frontend (Fetch API)
    GET  /api/health           -> Simple health check endpoint

Run with:
    python app.py
"""

from flask import Flask, render_template, request, jsonify

from config import Config
from grammar import GrammarChecker

app = Flask(__name__)
app.config.from_object(Config)

# The grammar engine is instantiated once and reused across requests.
# Because GrammarChecker.check() is a pure function of its input text,
# a single shared instance is safe to use across requests.
grammar_checker = GrammarChecker()


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Landing / home page."""
    return render_template("index.html")


@app.route("/checker")
def checker_page():
    """Main grammar-checking tool page."""
    return render_template("checker.html")


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/api/check-grammar", methods=["POST"])
def check_grammar():
    """
    Accepts JSON: {"text": "<user text>"}
    Returns JSON: {
        "original_text": "...",
        "corrected_text": "...",
        "mistakes": [{"original":..., "correction":..., "explanation":...}, ...],
        "stats": {"word_count":.., "character_count":.., "sentence_count":.., "mistakes_found":..}
    }
    """
    # --- Input validation -------------------------------------------------
    if not request.is_json:
        return jsonify({"error": "Request must have Content-Type: application/json"}), 400

    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Missing required field: 'text'"}), 400

    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "'text' must be a string"}), 400

    # Strip user input of any surrounding whitespace before validating length.
    text = text.strip()

    if len(text) < Config.MIN_TEXT_LENGTH:
        return jsonify({"error": "Text cannot be empty."}), 400

    if len(text) > Config.MAX_TEXT_LENGTH:
        return (
            jsonify(
                {
                    "error": (
                        f"Text exceeds maximum allowed length of "
                        f"{Config.MAX_TEXT_LENGTH} characters."
                    )
                }
            ),
            400,
        )

    # NOTE: We never execute or render user input as HTML/JS. It is treated
    # strictly as plain text data both here and on the frontend (see
    # script.js, which uses textContent rather than innerHTML for user text).
    try:
        result = grammar_checker.check(text)
    except Exception as exc:  # pragma: no cover - defensive guard
        app.logger.exception("Grammar check failed")
        return jsonify({"error": "Internal error while checking grammar."}), 500

    return jsonify(result), 200


@app.route("/api/health")
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(413)
def payload_too_large(_error):
    return jsonify({"error": "Request payload too large."}), 413


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="127.0.0.1", port=5000)
