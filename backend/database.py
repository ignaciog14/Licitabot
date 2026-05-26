from functools import lru_cache

from supabase import Client, create_client

from config import get_settings


@lru_cache
def get_db() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError(
            "Supabase no está configurado: revisa SUPABASE_URL y SUPABASE_SERVICE_KEY en .env"
        )
    return create_client(settings.supabase_url, settings.supabase_service_key)
