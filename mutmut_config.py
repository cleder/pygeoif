"""Mutmut configuration."""

files_to_mutate = ["pygeoif/geometry.py", "pygeoif/feature.py", "pygeoif/factories.py"]


def pre_mutation(context):
    if context.filename not in files_to_mutate:
        context.skip = True
