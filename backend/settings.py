import os

PREFERRED_MODELS = [
    "qwen2.5:3b",
    "llama3.2:3b",
    "gemma2:2b",
    "qwen3:8b",
    "deepseek-coder:6.7b",
    "phi3:mini",
    "hermes3:8b",
    "mistral",
    "llama3",
]

# Database path for SQLite chat history
SQLITE_DB_PATH = os.path.join("database", "copilot_history.db")

# Upload configurations
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".csv", ".xlsx"}
UPLOAD_DIR = os.path.join("scratch", "uploads")
