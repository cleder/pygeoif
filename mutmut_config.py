"""Mutmut configuration."""
from typing import Any

files_to_mutate = [
    "pygeoif/geometry.py",
    "pygeoif/feature.py",
    "pygeoif/factories.py",
    "pygeoif/functions.py",
]


def pre_mutation(context: Any) -> None:
    """Only include the files specified above."""
    if context.filename not in files_to_mutate:
        context.skip = True


__all__ = ["pre_mutation"]
