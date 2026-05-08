"""Pytest configuration and fixtures for SnapGit tests."""

import os
import sys
import tempfile
import shutil
import pytest

# Add snapgit to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from snapgit.commands.init_repo import init_repo
from snapgit.objects import create_blob, create_commit
from snapgit.refs import RefManager


@pytest.fixture
def temp_repo():
    """Create a temporary directory with initialized SnapGit repo."""
    tmpdir = tempfile.mkdtemp(prefix="snapgit_test_")
    original_cwd = os.getcwd()
    
    try:
        os.chdir(tmpdir)
        init_repo()
        yield tmpdir
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)


@pytest.fixture
def sample_commits(temp_repo):
    """Create sample commits in a repository."""
    # First commit
    blob1 = create_blob(b"file1 content v1")
    c1 = create_commit(
        message="first commit",
        parent=None,
        tree_data=f"file1.txt {blob1}\n",
        author="Test Author",
        date="1000000000"
    )
    RefManager.update_branch("main", c1)
    
    # Second commit
    blob2 = create_blob(b"file1 content v2")
    c2 = create_commit(
        message="second commit",
        parent=c1,
        tree_data=f"file1.txt {blob2}\n",
        author="Test Author",
        date="2000000000"
    )
    RefManager.update_branch("main", c2)
    
    # Third commit
    blob3 = create_blob(b"file2 content")
    c3 = create_commit(
        message="third commit",
        parent=c2,
        tree_data=f"file1.txt {blob2}\nfile2.txt {blob3}\n",
        author="Test Author",
        date="3000000000"
    )
    RefManager.update_branch("main", c3)
    
    return {
        "c1": c1,
        "c2": c2,
        "c3": c3,
        "blob1": blob1,
        "blob2": blob2,
        "blob3": blob3,
    }


@pytest.fixture
def branched_repo(sample_commits):
    """Create a repository with multiple branches."""
    commits = sample_commits
    
    # Create feature branch from first commit
    blob_feature = create_blob(b"feature content")
    c_feature = create_commit(
        message="feature work",
        parent=commits["c1"],
        tree_data=f"file1.txt {commits['blob1']}\nfeature.txt {blob_feature}\n",
        author="Feature Author",
        date="1500000000"
    )
    RefManager.create_branch("feature", commits["c1"])
    RefManager.update_branch("feature", c_feature)
    
    # Keep main at c3
    RefManager.set_head_to_branch("main")
    
    return {
        **commits,
        "c_feature": c_feature,
        "blob_feature": blob_feature,
    }


@pytest.fixture
def clean_repo():
    """Create a minimal empty repo for testing."""
    tmpdir = tempfile.mkdtemp(prefix="snapgit_clean_")
    original_cwd = os.getcwd()
    
    try:
        os.chdir(tmpdir)
        init_repo()
        yield tmpdir
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)
