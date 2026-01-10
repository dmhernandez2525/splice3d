"""
Splice3D Python Package Setup

Install with: pip install .
Or for development: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="splice3d",
    version="0.1.0",
    author="Splice3D Contributors",
    author_email="splice3d@example.com",
    description="Multi-color filament pre-splicer for FDM 3D printing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/splice3d",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/splice3d/issues",
        "Documentation": "https://github.com/yourusername/splice3d#readme",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Printing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=["postprocessor", "postprocessor.*", "cli", "cli.*"]),
    python_requires=">=3.9",
    install_requires=[
        "pyserial>=3.5",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "isort>=5.12",
        ],
    },
    entry_points={
        "console_scripts": [
            "splice3d=postprocessor.splice3d_postprocessor:main",
            "splice3d-analyze=cli.analyze_gcode:main",
            "splice3d-simulate=cli.simulator:main",
            "splice3d-validate=postprocessor.recipe_validator:validate_recipe",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.gcode", "*.json"],
    },
)
