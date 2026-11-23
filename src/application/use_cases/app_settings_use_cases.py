from typing import Optional

from src.domain.entities.app_settings import Language
from src.domain.entities.theme import DEFAULT_THEME_ID
from src.domain.repositories.app_settings_repository import AppSettingsRepository

THEME_KEY = "current_theme"
FONT_SIZE_KEY = "base_font_size"
DEFAULT_BASE_FONT_SIZE = 13  # mirrors src.presentation.theme.DEFAULT_BASE_FONT_SIZE
LANGUAGE_KEY = "language"


class AppSettingsUseCases:
    def __init__(self, app_settings_repository: AppSettingsRepository):
        self._repository = app_settings_repository

    def get_current_theme_id(self) -> str:
        return self._repository.get(THEME_KEY) or DEFAULT_THEME_ID

    def set_current_theme_id(self, theme_id: str) -> None:
        self._repository.set(THEME_KEY, theme_id)

    def get_base_font_size(self) -> int:
        raw = self._repository.get(FONT_SIZE_KEY)
        if raw is None:
            return DEFAULT_BASE_FONT_SIZE
        try:
            return int(raw)
        except ValueError:
            return DEFAULT_BASE_FONT_SIZE

    def set_base_font_size(self, size: int) -> None:
        self._repository.set(FONT_SIZE_KEY, str(size))

    def get_language(self) -> Optional[str]:
        """Return the persisted language code, or None if the user has not
        chosen one yet (first run). Callers resolve the first-run default from
        the OS locale, since locale detection belongs to the presentation
        layer (Qt), not here."""
        raw = self._repository.get(LANGUAGE_KEY)
        if raw is None:
            return None
        try:
            return Language(raw).value
        except ValueError:
            return None

    def set_language(self, language) -> None:
        value = language.value if isinstance(language, Language) else language
        self._repository.set(LANGUAGE_KEY, value)
