"""Application localization (i18n) runtime.

Mirrors the module-global, set-once-at-startup contract of
``src.presentation.theme``. Call :func:`load_language` exactly once in
``main()`` - after ``AppSettingsUseCases`` exists but before any widget is
constructed. Every read-site does ``from src.presentation.i18n import t`` and
reads through it inside a function body, so it naturally picks up the loaded
language with zero per-file wiring.

Language changes apply on restart (same flow as theme/font), so there is no
live re-translation to worry about.
"""

from PySide6.QtCore import QLocale

from src.presentation.translations import en as _en
from src.presentation.translations import es as _es
from src.presentation.translations import pt_BR as _pt_br

# Supported UI languages. Keys are the values persisted in app_settings.
SUPPORTED_LANGUAGES = ("en", "pt_BR", "es")
DEFAULT_LANGUAGE = "en"

_CATALOGS = {
    "en": _en.TRANSLATIONS,
    "pt_BR": _pt_br.TRANSLATIONS,
    "es": _es.TRANSLATIONS,
}

_QLOCALES = {
    "en": QLocale(QLocale.Language.English, QLocale.Country.UnitedStates),
    "pt_BR": QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil),
    "es": QLocale(QLocale.Language.Spanish, QLocale.Country.Spain),
}

# --- module globals mutated by load_language() -----------------------------
_LANG = DEFAULT_LANGUAGE
_CATALOG = _CATALOGS[DEFAULT_LANGUAGE]


def load_language(lang: str) -> None:
    """Set the active UI language and Qt locale.

    Restart-only i18n: call once, in ``main()``, after ``AppSettingsUseCases``
    exists but before any widget/icon is constructed. Also sets the default
    ``QLocale`` so Qt input widgets (``QDateEdit``) inherit locale-correct
    date formats automatically.
    """
    global _LANG, _CATALOG
    if lang not in _CATALOGS:
        lang = DEFAULT_LANGUAGE
    _LANG = lang
    _CATALOG = _CATALOGS[lang]
    QLocale.setDefault(_QLOCALES[lang])


def current_language() -> str:
    return _LANG


def detect_default_language() -> str:
    """Resolve a first-run default from the OS locale, falling back to English.

    Portuguese -> pt_BR, Spanish -> es, anything else -> en.
    """
    language = QLocale.system().language()
    if language == QLocale.Language.Portuguese:
        return "pt_BR"
    if language == QLocale.Language.Spanish:
        return "es"
    return DEFAULT_LANGUAGE


def t(key: str, **kwargs) -> str:
    """Look up a translation key, formatting with ``kwargs`` if provided.

    Falls back to the English catalog, then to the key itself, so a missing
    translation degrades gracefully instead of crashing.
    """
    template = _CATALOG.get(key)
    if template is None:
        template = _CATALOGS["en"].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return template
    return template
