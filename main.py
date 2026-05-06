"""
SnapGit CLI entry point.

This module serves as the application's entry point. It delegates all
command routing and execution logic to the snapgit.cli module.
"""

from snapgit.cli import main


if __name__ == "__main__":
    main()
