"""
TalentLens AI - Configuration
Central place for app settings, so nothing important is hard-coded
inside app.py or the modules.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'talentlens.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads (kept outside /static so resumes are never publicly served)
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB per request (multiple resumes)

    # Scoring weights (must sum to 1.0) — kept configurable, not hard-coded
    # in the scoring logic itself.
    SCORE_WEIGHTS = {
        "semantic_match": 0.45,
        "required_skills": 0.25,
        "experience": 0.15,
        "education": 0.10,
        "certifications": 0.05,
    }

    # NLP
    SPACY_MODEL = "en_core_web_sm"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, fast Sentence-Transformers model