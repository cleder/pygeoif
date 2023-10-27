"""Mutmut configuration."""
from typing import Protocol

files_to_mutate = [
    "pygeoif/geometry.py",
    "pygeoif/feature.py",
    "pygeoif/factories.py",
    "pygeoif/functions.py",
]


class Context(Protocol):
    filename: str
    skip: bool


def pre_mutation(context: Context) -> None:
    """Only include the files specified above."""
    if context.filename not in files_to_mutate:
        context.skip = True


__all__ = ["pre_mutation"]
