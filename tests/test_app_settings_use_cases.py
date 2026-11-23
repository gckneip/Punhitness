from src.application.use_cases.app_settings_use_cases import AppSettingsUseCases, DEFAULT_BASE_FONT_SIZE
from src.domain.entities.app_settings import Language
from src.domain.entities.theme import DEFAULT_THEME_ID
from tests._fakes import FakeAppSettingsRepo


def _use_cases():
    return AppSettingsUseCases(FakeAppSettingsRepo())


def test_defaults_when_nothing_persisted():
    uc = _use_cases()
    assert uc.get_current_theme_id() == DEFAULT_THEME_ID
    assert uc.get_base_font_size() == DEFAULT_BASE_FONT_SIZE


def test_set_and_get_theme_id_round_trips():
    uc = _use_cases()
    uc.set_current_theme_id("builtin:dark")
    assert uc.get_current_theme_id() == "builtin:dark"


def test_set_and_get_font_size_round_trips():
    uc = _use_cases()
    uc.set_base_font_size(18)
    assert uc.get_base_font_size() == 18


def test_corrupt_font_size_falls_back_to_default():
    repo = FakeAppSettingsRepo()
    repo.set("base_font_size", "not-a-number")
    uc = AppSettingsUseCases(repo)
    assert uc.get_base_font_size() == DEFAULT_BASE_FONT_SIZE


def test_language_is_none_on_first_run():
    uc = _use_cases()
    assert uc.get_language() is None


def test_set_and_get_language_round_trips_with_a_string_code():
    uc = _use_cases()
    uc.set_language("pt_BR")
    assert uc.get_language() == "pt_BR"


def test_set_language_accepts_a_language_enum_member():
    uc = _use_cases()
    uc.set_language(Language.SPANISH)
    assert uc.get_language() == "es"


def test_corrupt_language_falls_back_to_none():
    repo = FakeAppSettingsRepo()
    repo.set("language", "xx-not-a-real-language")
    uc = AppSettingsUseCases(repo)
    assert uc.get_language() is None
