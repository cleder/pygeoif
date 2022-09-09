"""Setup script."""
import os
import sys
from typing import Any
from typing import List

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand  # noqa: N812


class PyTest(TestCommand):
    """Run the tests with PyTest."""

    def finalize_options(self) -> None:
        TestCommand.finalize_options(self)
        self.test_args: List[Any] = []
        self.test_suite = True

    def run_tests(self) -> None:
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


version = "1.0.beta.13"

with open("README.rst", encoding="utf-8") as readme:
    README = readme.read()
with open(os.path.join("docs", "HISTORY.txt"), encoding="utf-8") as changelog:
    HISTORY = changelog.read()

setup(
    name="pygeoif",
    version=version,
    description="A basic implementation of the __geo_interface__",
    long_description=README + "\n" + HISTORY,
    classifiers=[
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Development Status :: 4 - Beta",
        # Development Status :: 5 - Production/Stable
        "Operating System :: OS Independent",
    ],
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="GIS Spatial WKT",
    author="Christian Ledermann",
    author_email="christian.ledermann@gmail.com",
    url="https://github.com/cleder/pygeoif/",
    license="LGPL",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    tests_require=["pytest"],
    install_requires=["typing_extensions"],
    python_requires=">=3.7",
    cmdclass={"test": PyTest},
    entry_points="""
      # -*- Entry points: -*-
      """,
)

__all__ = ["version"]
