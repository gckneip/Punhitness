"""Localized display labels for domain enums and the seeded exercise catalog.

The enum *values* (and exercise names) stay in the database unchanged
(English/machine strings); only their on-screen display is translated. Each
helper accepts either an enum member or its raw ``.value`` string (render
sites have both), and returns the localized label, falling back to the raw
value for anything unknown.
"""

import re

from src.application.exercise_presets import DEFAULT_EXERCISES
from src.domain.entities.exercise import MuscleGroup
from src.presentation.i18n import t


def _value(item):
    return item.value if hasattr(item, "value") else item


def muscle_group_label(item) -> str:
    value = _value(item)
    try:
        key = MuscleGroup(value).name.lower()
    except ValueError:
        return value
    return t(f"enum.muscle_group.{key}")


def muscle_group_choices():
    """(enum, label) pairs for populating a MuscleGroup combo."""
    return [(m, muscle_group_label(m)) for m in MuscleGroup]


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    return _SLUG_RE.sub("_", name.strip().lower()).strip("_")


# Only the seeded default catalog (src/application/exercise_presets.py) has a
# stable identity to translate "when possible" — a user-renamed or custom
# exercise name is arbitrary text with nothing to look up, so it isn't in
# this map and exercise_name_label() returns it unchanged.
_EXERCISE_NAME_KEYS = {preset.name: f"exercise_name.{_slugify(preset.name)}" for preset in DEFAULT_EXERCISES}


def exercise_name_label(name: str) -> str:
    key = _EXERCISE_NAME_KEYS.get(name)
    return t(key) if key else name
