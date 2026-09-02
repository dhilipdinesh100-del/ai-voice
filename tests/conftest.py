import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from fastapi.testclient import TestClient

from app.config import settings
test_data_dir = settings.BASE_DIR / "data" / "test_data"
test_data_dir.mkdir(parents=True, exist_ok=True)
settings.DATABASE_PATH = test_data_dir / "test_nova.db"
settings.AUDIO_DIR = test_data_dir / "audio"
settings.UPLOAD_DIR = test_data_dir / "uploads"
settings.init_directories()

from app.database.session import init_db
init_db()

from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
