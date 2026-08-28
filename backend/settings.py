import os

# Preferred Ollama models in order of priority
PREFERRED_MODELS = [
    "qwen3",
    "qwen2.5:3b",
    "qwen2.5",
    "mistral",
    "llama3.1",
    "llama3.2",
    "llama3",
    "phi3",
    "phi",
    "gemma2",
    "gemma"
]

# Database path for SQLite chat history
SQLITE_DB_PATH = os.path.join("database", "copilot_history.db")

# Upload configurations
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".csv", ".xlsx"}
UPLOAD_DIR = os.path.join("scratch", "uploads")
