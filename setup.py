"""SnapGit setup configuration (backward compatibility)."""

from setuptools import setup, find_packages

setup(
    name="snapgit",
    version="0.5.0",
    description="Git-like version control system built from scratch in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="SnapGit Author",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests"]),
    entry_points={
        "console_scripts": [
            "snapgit=snapgit.cli:main",
        ],
    },
    extras_require={
        "dev": ["pytest>=7.0", "pytest-cov>=4.0"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Version Control",
    ],
)
