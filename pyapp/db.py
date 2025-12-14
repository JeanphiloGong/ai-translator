from pyapp.repositories.sqlite_repo import TranslationRepository
from pyapp.settings import get_settings


def init_repository() -> TranslationRepository:
    """Initialize repository with current settings (ensures schema)."""
    settings = get_settings()
    return TranslationRepository(settings.database_path)

