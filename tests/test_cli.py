"""Tests for SnapGit CLI interface."""

import pytest


class TestCLIInterface:
    """Test CLI main interface."""
    
    def test_cli_structure_exists(self, temp_repo):
        """Test that CLI module can be imported."""
        from snapgit import cli
        assert hasattr(cli, 'main')

