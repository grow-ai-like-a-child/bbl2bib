#!/usr/bin/env python3
"""Setup script for bbl2bib."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="bbl2bib",
    version="1.0.0",
    author="BBL2BIB Contributors",
    description="Convert BBL files back to BIB format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bbl2bib",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "bbl2bib=bbl2bib:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="bibtex, latex, bibliography, bbl, bib, converter",
)
