import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.database.session import get_db_connection

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "dark",
    "assistant_name": "NOVA",
    "personality": "Futuristic",
    "custom_prompt": "",
    "voice": "alloy",
    "voice_speed": 1.0,
    "language": "en",
    "auto_play": True,
    "hands_free": False,
    "memory_enabled": True,
    "save_conversations": True,
    "save_audio": False,
    "response_length": "medium"
}

class SettingsRepository:
    @staticmethod
    def get_all() -> Dict[str, Any]:
        result = dict(DEFAULT_SETTINGS)
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT key, value FROM settings")
            for row in cursor.fetchall():
                try:
                    result[row["key"]] = json.loads(row["value"])
                except Exception:
                    result[row["key"]] = row["value"]
        return result

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if not row:
                return DEFAULT_SETTINGS.get(key, default)
            try:
                return json.loads(row["value"])
            except Exception:
                return row["value"]

    @staticmethod
    def update(settings_dict: Dict[str, Any]) -> Dict[str, Any]:
        now = utc_now_iso()
        with get_db_connection() as conn:
            for k, v in settings_dict.items():
                val_str = json.dumps(v)
                conn.execute(
                    """INSERT INTO settings (key, value, updated_at) 
                       VALUES (?, ?, ?) 
                       ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at""",
                    (k, val_str, now)
                )
        return SettingsRepository.get_all()
