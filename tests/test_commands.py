"""Tests for SnapGit CLI commands."""

import pytest
import os
from snapgit.commands.init_repo import init_repo
from snapgit.commands.add_file import add_file
from snapgit.commands.commit import create_commit
from snapgit.commands.branch import create_branch, list_branches
from snapgit.commands.checkout import checkout
from snapgit.commands.diff import diff as diff_cmd
from snapgit.commands.merge import merge as merge_cmd
from snapgit.refs import RefManager
from snapgit.graph import CommitGraph


class TestInitCommand:
    """Test init_repo command."""
    
    def test_init_creates_structure(self, clean_repo):
        """Test that init creates .snapgit directory structure."""
        assert os.path.exists(".snapgit")
        assert os.path.exists(".snapgit/objects")
        assert os.path.exists(".snapgit/refs/heads")
        assert os.path.exists(".snapgit/HEAD")


class TestCommitCommand:
    """Test commit command."""
    
    def test_simple_workflow(self, temp_repo):
        """Test simple add and commit workflow."""
        # Create a test file
        with open("test.txt", "w") as f:
            f.write("test content")
        
        add_file("test.txt")
        create_commit("First commit")
        
        # Verify commit was created
        _, current_branch = RefManager.resolve_head()
        current_commit = RefManager.get_branch_commit(current_branch)
        
        assert current_commit is not None
        node = CommitGraph.parse_commit(current_commit)
        assert "First commit" in node.message


class TestBranchCommand:
    """Test branch operations."""
    
    def test_create_branch(self, sample_commits):
        """Test creating branches."""
        RefManager.set_head_to_branch("main")
        create_branch("feature")
        
        assert RefManager.branch_exists("feature")
    
    def test_list_branches(self, sample_commits):
        """Test listing branches."""
        RefManager.create_branch("feature", sample_commits["c1"])
        RefManager.create_branch("develop", sample_commits["c1"])
        
        branches = RefManager.list_branches()
        assert "main" in branches
        assert "feature" in branches
        assert "develop" in branches


class TestCheckoutCommand:
    """Test checkout operations."""
    
    def test_checkout_branch(self, branched_repo):
        """Test switching branches."""
        RefManager.set_head_to_branch("main")
        checkout("feature")
        
        _, current = RefManager.resolve_head()
        assert current == "feature"
    
    def test_checkout_detached(self, sample_commits):
        """Test detached HEAD checkout."""
        commit_hash = sample_commits["c1"]
        checkout(commit_hash)
        
        current_commit, branch = RefManager.resolve_head()
        assert current_commit == commit_hash
        assert branch is None


class TestDiffCommand:
    """Test diff command."""
    
    def test_diff_two_commits(self, sample_commits):
        """Test diffing between commits."""
        c1 = sample_commits["c1"]
        c2 = sample_commits["c2"]
        
        # This calls the diff command
        # It should show differences between c1 and c2
        # We're testing it doesn't crash
        try:
            diff_cmd(c1, c2)
        except SystemExit:
            pass  # Commands may call sys.exit


class TestMergeCommand:
    """Test merge command."""
    
    def test_merge_branches(self, branched_repo):
        """Test merging branches."""
        RefManager.set_head_to_branch("main")
        
        # This should work without raising exceptions
        try:
            merge_cmd("feature")
        except SystemExit:
            pass  # Commands may call sys.exit


class TestIntegrationWorkflows:
    """Test complete workflows."""
    
    def test_workflow_simple(self, temp_repo):
        """Test simple linear workflow."""
        # Create and commit two files
        with open("file1.txt", "w") as f:
            f.write("content1")
        
        add_file("file1.txt")
        create_commit("First file")
        
        with open("file2.txt", "w") as f:
            f.write("content2")
        
        add_file("file2.txt")
        create_commit("Second file")
        
        # Verify history
        _, branch = RefManager.resolve_head()
        commit_hash = RefManager.get_branch_commit(branch)
        history = CommitGraph.get_history(commit_hash)
        
        assert len(history) >= 2
    
    def test_workflow_branching(self, temp_repo):
        """Test branching and merging workflow."""
        # Create initial commit
        with open("base.txt", "w") as f:
            f.write("base")
        
        add_file("base.txt")
        create_commit("Base commit")
        
        # Create feature branch
        create_branch("feature")
        checkout("feature")
        
        with open("feature.txt", "w") as f:
            f.write("feature")
        
        add_file("feature.txt")
        create_commit("Feature work")
        
        # Switch back to main
        checkout("main")
        
        # Verify we're on main
        _, current = RefManager.resolve_head()
        assert current == "main"
        
        # Feature branch still exists
        assert RefManager.branch_exists("feature")
