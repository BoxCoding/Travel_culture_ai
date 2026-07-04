import json
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import get_settings


@lru_cache
def get_firestore_client():
    settings = get_settings()

    if not firebase_admin._apps:
        if settings.firebase_service_account_json:
            cred = credentials.Certificate(json.loads(settings.firebase_service_account_json))
        else:
            # Falls back to GOOGLE_APPLICATION_CREDENTIALS env var / ADC (useful for local dev).
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

    return firestore.client()
