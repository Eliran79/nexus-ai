# nexus-ai/setup.py
from setuptools import setup, find_packages

setup(
    name="nexus-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["anthropic", "prompt_toolkit", "pygments"],
    entry_points={
        "console_scripts": [
            "nexus-ai=nexus_ai.main:main",  # Changed from nexus to nexus-ai
        ],
    },
)
