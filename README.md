# AI Translator

Lightweight translation tooling that turns Chinese or English input into polished English and Japanese output, with optional grammar notes, and saves every run to SQLite for later reference.

## What it does
- Translate Chinese to English and Japanese, including Hiragana for the Japanese output.
- Correct English sentences and provide Japanese translations.
- Add English/Japanese grammar explanations when requested.
- Persist translation results to a local SQLite database.

## Project layout
- `pyapp/`: Python implementation (FastAPI service and Typer CLI).
- `translations.db`: Default SQLite database (auto-created on first run).
- `requirements.txt`: Python dependencies.
- `ai-translator`: Convenience wrapper script for the CLI (bash).
- `goapp/`: Placeholder for a Go implementation (currently empty).

## Prerequisites
- Python 3.9+ recommended.
- An OpenAI API key (`OPENAI_API_KEY`).

## Setup
1) Clone the repo  
```bash
git clone https://github.com/JeanphiloGong/ai-translator.git
cd ai-translator
```
2) (Optional) create & activate a virtualenv (this guide uses `pyapp/.venv`)  
```bash
python -m venv pyapp/.venv
source pyapp/.venv/bin/activate  # Windows: pyapp\\.venv\\Scripts\\activate
```
3) Install dependencies  
```bash
pip install -r requirements.txt
```
4) Configure environment variables in `.env` (auto-loaded):
```env
OPENAI_API_KEY=sk-...
# Optional overrides:
# OPENAI_BASE_URL=https://api.chatanywhere.tech/v1
# OPENAI_MODEL=gpt-4o-2024-08-06
# DB_PATH=translations.db
```

## Run the CLI
Use the Typer commands via the module entrypoint:
```bash
# Translate Chinese (add --grammar to include explanations)
python -m pyapp translate-zh "你好世界" --grammar

# Correct English and translate to Japanese
python -m pyapp correct-en "This are a cat" --grammar
```
Results print to stdout and are stored in the SQLite database.

## Shortcut script
Already included in repo root: `ai-translator` (bash). It auto-activates `pyapp/.venv`, sets `DB_PATH` to `translations.db` in the project root, and runs any Typer subcommand.

- Make it executable (once):  
```bash
chmod +x ai-translator
```
- (Optional) symlink to your PATH for global use:  
```bash
ln -sf "$PWD/ai-translator" ~/bin/ai-translator  # ensure ~/bin is in PATH
```
- The script resolves symlinks, so using it from `~/bin` still picks the project venv/DB.
- Usage from any directory:  
```bash
ai-translator translate-zh "你好世界" --grammar
ai-translator correct-en "This are a cat" --grammar
```

## Run the API server
Start FastAPI with Uvicorn:
```bash
uvicorn pyapp.api.main:app --reload
```
- Health check: `GET http://127.0.0.1:8000/health`
- Translate Chinese:  
```bash
curl -X POST http://127.0.0.1:8000/translate/chinese \
  -H "Content-Type: application/json" \
  -d '{"text":"你好世界","include_grammar":true}'
```
- Correct English:  
```bash
curl -X POST http://127.0.0.1:8000/correct/english \
  -H "Content-Type: application/json" \
  -d '{"text":"This are a cat","include_grammar":true}'
```

The API and CLI both share the same settings and database location configured via `.env`.
