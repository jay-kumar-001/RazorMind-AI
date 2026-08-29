import sqlite3
import json
import threading
from datetime import datetime
from backend.settings import SQLITE_DB_PATH

_lock = threading.Lock()


class ChatHistoryService:
    def __init__(self):
        self.db_path = SQLITE_DB_PATH
        self.init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=8.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def init_db(self):
        import os
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    personality TEXT NOT NULL,
                    merchant_id TEXT,
                    model_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens INTEGER,
                    latency REAL,
                    agents_consulted TEXT,
                    model_used TEXT,
                    file_name TEXT,
                    file_content TEXT,
                    parent_id TEXT,
                    version INTEGER DEFAULT 1,
                    is_current INTEGER DEFAULT 1,
                    edited INTEGER DEFAULT 0,
                    stopped INTEGER DEFAULT 0,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            self._ensure_column(cursor, "messages", "parent_id", "TEXT")
            self._ensure_column(cursor, "messages", "version", "INTEGER DEFAULT 1")
            self._ensure_column(cursor, "messages", "is_current", "INTEGER DEFAULT 1")
            self._ensure_column(cursor, "messages", "edited", "INTEGER DEFAULT 0")
            self._ensure_column(cursor, "messages", "stopped", "INTEGER DEFAULT 0")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_parent ON messages(parent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_content ON messages(conversation_id)")
            conn.commit()
            conn.close()

    @staticmethod
    def _ensure_column(cursor, table, column, ddl):
        cursor.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cursor.fetchall()}
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")

    def create_conversation(self, conv_id, title, mode, personality, merchant_id=None, model_used=None) -> dict:
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT INTO conversations (id, title, mode, personality, merchant_id, model_used, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (conv_id, title, mode, personality, merchant_id, model_used, now, now),
            )
            conn.commit()
            conn.close()
        return {
            "id": conv_id,
            "title": title,
            "mode": mode,
            "personality": personality,
            "merchant_id": merchant_id,
            "model_used": model_used,
            "created_at": now,
            "updated_at": now,
        }

    def get_conversation(self, conv_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def list_conversations(self) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_conversation_title(self, conv_id: str, title: str):
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, conv_id),
            )
            conn.commit()
            conn.close()

    def update_conversation_settings(self, conv_id: str, mode=None, personality=None, merchant_id=None, model_used=None):
        conv = self.get_conversation(conv_id)
        if not conv:
            return None
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                UPDATE conversations
                SET mode = ?, personality = ?, merchant_id = ?, model_used = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    mode if mode is not None else conv["mode"],
                    personality if personality is not None else conv["personality"],
                    merchant_id if merchant_id is not None else conv["merchant_id"],
                    model_used if model_used is not None else conv["model_used"],
                    now,
                    conv_id,
                ),
            )
            conn.commit()
            conn.close()
        return self.get_conversation(conv_id)

    def delete_conversation(self, conv_id: str):
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
            conn.commit()
            conn.close()

    def clear_all_conversations(self):
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM conversations")
            conn.commit()
            conn.close()

    def add_message(
        self,
        msg_id,
        conv_id,
        role,
        content,
        tokens=None,
        latency=None,
        agents_consulted=None,
        model_used=None,
        file_name=None,
        file_content=None,
        parent_id=None,
        version=1,
        is_current=1,
        edited=0,
        stopped=0,
    ) -> dict:
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            agents_str = json.dumps(agents_consulted) if agents_consulted else None
            cursor.execute(
                """
                INSERT INTO messages (
                    id, conversation_id, role, content, timestamp, tokens, latency,
                    agents_consulted, model_used, file_name, file_content,
                    parent_id, version, is_current, edited, stopped
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    msg_id, conv_id, role, content, now, tokens, latency, agents_str,
                    model_used, file_name, file_content, parent_id, version, is_current,
                    edited, stopped,
                ),
            )
            cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
            conn.commit()
            conn.close()
        return {
            "id": msg_id,
            "conversation_id": conv_id,
            "role": role,
            "content": content,
            "timestamp": now,
            "tokens": tokens,
            "latency": latency,
            "agents_consulted": agents_consulted or [],
            "model_used": model_used,
            "file_name": file_name,
            "file_content": file_content,
            "parent_id": parent_id,
            "version": version,
            "is_current": is_current,
            "edited": edited,
            "stopped": stopped,
        }

    def _hydrate(self, r) -> dict:
        m = dict(r)
        if m.get("agents_consulted"):
            try:
                m["agents_consulted"] = json.loads(m["agents_consulted"])
            except Exception:
                m["agents_consulted"] = []
        else:
            m["agents_consulted"] = []
        m["is_current"] = int(m.get("is_current") if m.get("is_current") is not None else 1)
        m["version"] = int(m.get("version") or 1)
        m["edited"] = int(m.get("edited") or 0)
        m["stopped"] = int(m.get("stopped") or 0)
        return m

    def get_messages(self, conv_id: str, current_only: bool = False, limit: int = None, before: str = None) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        clauses = ["conversation_id = ?"]
        params = [conv_id]
        if current_only:
            clauses.append("(is_current = 1 OR is_current IS NULL)")
        if before:
            clauses.append("timestamp < ?")
            params.append(before)
        where = " AND ".join(clauses)
        sql = f"SELECT * FROM messages WHERE {where} ORDER BY timestamp DESC"
        fetch_limit = None
        if limit:
            fetch_limit = int(limit) + 1
            sql += " LIMIT ?"
            params.append(fetch_limit)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        messages = [self._hydrate(r) for r in rows]
        has_more = False
        if limit and len(messages) > limit:
            has_more = True
            messages = messages[:limit]
        messages.reverse()
        return {"messages": messages, "has_more": has_more}

    def get_message(self, msg_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
        row = cursor.fetchone()
        conn.close()
        return self._hydrate(row) if row else None

    def get_versions(self, parent_id: str) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM messages WHERE parent_id = ? ORDER BY version ASC",
            (parent_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [self._hydrate(r) for r in rows]

    def update_message_content(self, msg_id: str, content: str, edited: int = 1):
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE messages SET content = ?, edited = ? WHERE id = ?",
                (content, edited, msg_id),
            )
            conn.commit()
            conn.close()

    def delete_message(self, msg_id: str, conv_id: str = None) -> bool:
        msg = self.get_message(msg_id)
        if not msg:
            return False
        if conv_id and msg["conversation_id"] != conv_id:
            return False
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            if msg["role"] == "user":
                cursor.execute(
                    "DELETE FROM messages WHERE parent_id = ? OR id = ?",
                    (msg_id, msg_id),
                )
            else:
                cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
            conn.commit()
            conn.close()
        return True

    def delete_messages_after(self, conv_id: str, timestamp: str):
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM messages WHERE conversation_id = ? AND timestamp > ?",
                (conv_id, timestamp),
            )
            conn.commit()
            conn.close()

    def mark_not_current(self, msg_id: str):
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET is_current = 0 WHERE id = ?", (msg_id,))
            conn.commit()
            conn.close()

    def set_current_version(self, parent_id: str, msg_id: str):
        with _lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET is_current = 0 WHERE parent_id = ?", (parent_id,))
            if msg_id and msg_id != "__none__":
                cursor.execute("UPDATE messages SET is_current = 1 WHERE id = ?", (msg_id,))
            conn.commit()
            conn.close()

    def next_version_index(self, parent_id: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) FROM messages WHERE parent_id = ?", (parent_id,))
        row = cursor.fetchone()
        conn.close()
        current = row[0] if row and row[0] is not None else 0
        return int(current) + 1

    def search_conversations_and_messages(self, query: str) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        like_query = f"%{query}%"
        cursor.execute(
            """
            SELECT DISTINCT c.id, c.title, c.mode, c.personality, c.merchant_id, c.model_used, c.created_at, c.updated_at
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.title LIKE ? OR m.content LIKE ?
            ORDER BY c.updated_at DESC
            LIMIT 100
            """,
            (like_query, like_query),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]


chat_history_service = ChatHistoryService()
