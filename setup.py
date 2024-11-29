from importlib.metadata import entry_points

from setuptools import setup, find_packages

setup(
    name="python-flexseal",
    version="0.1.0",
    description="Generate a reproducible lock file from python package installations",
    author="Janrupf",
    author_email="business.janrupf@gmail.com",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "python-flexseal=flexseal.__main__:main",
        ]
    }
)
