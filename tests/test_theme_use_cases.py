import json

from src.application.use_cases.theme_use_cases import ThemeUseCases
from src.domain.entities.theme import BUILTIN_PREFIX, CUSTOM_PREFIX, LIGHT_PALETTE
from src.infrastructure.theming.theme_parser import ThemeParseError
from tests._fakes import FakeThemeRepo

DARK_JSON = json.dumps({
    "name": "Dark",
    "base": "light",
    "bg_app": "#14161c",
    "surface": "#1e212b",
    "border": "#2c303c",
    "text_primary": "#e6e8ef",
    "text_secondary": "#9aa0ae",
    "primary": "#5b8df9",
    "primary_hover": "#729bfa",
    "primary_pressed": "#3f6fd6",
    "selection": "#2d3a5c",
})


def test_list_available_themes_includes_light_and_builtins():
    uc = ThemeUseCases(FakeThemeRepo(builtins={"dark": DARK_JSON}))
    themes = uc.list_available_themes()
    theme_ids = {t.theme_id for t in themes}
    assert f"{BUILTIN_PREFIX}light" in theme_ids
    assert f"{BUILTIN_PREFIX}dark" in theme_ids


def test_resolve_light_palette_returns_the_canonical_instance():
    uc = ThemeUseCases(FakeThemeRepo())
    assert uc.resolve_palette(f"{BUILTIN_PREFIX}light") is LIGHT_PALETTE


def test_resolve_builtin_palette_parses_its_colors():
    uc = ThemeUseCases(FakeThemeRepo(builtins={"dark": DARK_JSON}))
    palette = uc.resolve_palette(f"{BUILTIN_PREFIX}dark")
    assert palette.name == "Dark"
    assert palette.bg_app == "#14161c"


def test_resolve_unknown_theme_id_returns_none():
    uc = ThemeUseCases(FakeThemeRepo())
    assert uc.resolve_palette(f"{BUILTIN_PREFIX}nonexistent") is None
    assert uc.resolve_palette(f"{CUSTOM_PREFIX}missing.json") is None
    assert uc.resolve_palette("") is None


def test_import_theme_file_saves_canonical_json_and_lists_it(tmp_path):
    source = tmp_path / "my-theme.json"
    source.write_text(json.dumps({"name": "My Theme", "primary": "#112233"}))

    uc = ThemeUseCases(FakeThemeRepo())
    result = uc.import_theme_file(str(source))

    assert result.theme_id == f"{CUSTOM_PREFIX}my-theme.json"
    assert result.name == "My Theme"
    assert any("missing" in w for w in result.warnings)

    palette = uc.resolve_palette(result.theme_id)
    assert palette.primary == "#112233"
    assert any(t.theme_id == result.theme_id and t.is_custom for t in uc.list_available_themes())


def test_import_theme_file_rejects_invalid_json(tmp_path):
    source = tmp_path / "broken.json"
    source.write_text("not json")

    uc = ThemeUseCases(FakeThemeRepo())
    try:
        uc.import_theme_file(str(source))
        assert False, "expected ThemeParseError"
    except ThemeParseError:
        pass
