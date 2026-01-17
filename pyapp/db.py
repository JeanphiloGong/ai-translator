from pyapp.repositories.sqlite_repo import TranslationRepository
from pyapp.repositories.task_repo import TaskRepository
from pyapp.settings import get_settings


def init_repository() -> TranslationRepository:
    """Initialize repository with current settings (ensures schema)."""
    settings = get_settings()
    return TranslationRepository(settings.database_path)


def init_task_repository() -> TaskRepository:
    """Initialize task repository with current settings (ensures schema)."""
    settings = get_settings()
    return TaskRepository(settings.database_path)
