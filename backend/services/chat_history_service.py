import sqlite3
import json
import uuid
from datetime import datetime
from backend.settings import SQLITE_DB_PATH

class ChatHistoryService:
    def __init__(self):
        self.db_path = SQLITE_DB_PATH
        self.init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create Conversations table
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

        # Create Messages table
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
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()

    def create_conversation(self, conv_id: str, title: str, mode: str, personality: str, merchant_id: str = None, model_used: str = None) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO conversations (id, title, mode, personality, merchant_id, model_used, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (conv_id, title, mode, personality, merchant_id, model_used, now, now))
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
            "updated_at": now
        }

    def get_conversation(self, conv_id: str) -> dict:
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
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            UPDATE conversations 
            SET title = ?, updated_at = ?
            WHERE id = ?
        """, (title, now, conv_id))
        conn.commit()
        conn.close()

    def delete_conversation(self, conv_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        conn.commit()
        conn.close()

    def clear_all_conversations(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()

    def add_message(self, msg_id: str, conv_id: str, role: str, content: str, 
                    tokens: int = None, latency: float = None, agents_consulted: list = None,
                    model_used: str = None, file_name: str = None, file_content: str = None) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        agents_str = json.dumps(agents_consulted) if agents_consulted else None
        
        cursor.execute("""
            INSERT INTO messages (id, conversation_id, role, content, timestamp, tokens, latency, agents_consulted, model_used, file_name, file_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, conv_id, role, content, now, tokens, latency, agents_str, model_used, file_name, file_content))
        
        # Touch updated_at for conversation
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
            "agents_consulted": agents_consulted,
            "model_used": model_used,
            "file_name": file_name,
            "file_content": file_content
        }

    def get_messages(self, conv_id: str) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conv_id,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for r in rows:
            m = dict(r)
            if m["agents_consulted"]:
                try:
                    m["agents_consulted"] = json.loads(m["agents_consulted"])
                except Exception:
                    m["agents_consulted"] = []
            else:
                m["agents_consulted"] = []
            messages.append(m)
        return messages

    def search_conversations_and_messages(self, query: str) -> list:
        conn = self._get_connection()
        cursor = conn.cursor()
        # Search in messages content or conversation titles
        like_query = f"%{query}%"
        cursor.execute("""
            SELECT DISTINCT c.id, c.title, c.mode, c.personality, c.merchant_id, c.updated_at
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.title LIKE ? OR m.content LIKE ?
            ORDER BY c.updated_at DESC
        """, (like_query, like_query))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

chat_history_service = ChatHistoryService()
