"""Localized display labels for domain enums.

The enum *values* stay in the database unchanged (English/machine strings); only
their on-screen display is translated. Each helper accepts either an enum member
or its raw ``.value`` string (render sites have both), and returns the localized
label, falling back to the raw value for anything unknown.
"""

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
