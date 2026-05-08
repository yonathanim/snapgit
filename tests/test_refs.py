"""Tests for SnapGit reference management."""

import pytest
from snapgit.refs import RefManager
from snapgit.objects import create_commit


class TestRefManager:
    """Test RefManager functionality."""
    
    def test_resolve_head_main_branch(self, clean_repo):
        """Test resolving HEAD on main branch."""
        commit, branch = RefManager.resolve_head()
        assert branch == "main"
        assert commit is None  # No commits yet
    
    def test_set_head_to_branch(self, clean_repo):
        """Test switching to a branch."""
        RefManager.set_head_to_branch("main")
        commit, branch = RefManager.resolve_head()
        assert branch == "main"
    
    def test_set_head_detached(self, sample_commits):
        """Test detached HEAD state."""
        commit_hash = sample_commits["c1"]
        RefManager.set_head_detached(commit_hash)
        
        commit, branch = RefManager.resolve_head()
        assert commit == commit_hash
        assert branch is None
    
    def test_create_branch(self, sample_commits):
        """Test creating a new branch."""
        c1 = sample_commits["c1"]
        RefManager.create_branch("feature", c1)
        
        assert RefManager.branch_exists("feature")
        commit = RefManager.get_branch_commit("feature")
        assert commit == c1
    
    def test_create_duplicate_branch(self, sample_commits):
        """Test that creating duplicate branch fails."""
        c1 = sample_commits["c1"]
        RefManager.create_branch("feature", c1)
        
        with pytest.raises(ValueError):
            RefManager.create_branch("feature", c1)
    
    def test_list_branches(self, sample_commits):
        """Test listing branches."""
        c1 = sample_commits["c1"]
        RefManager.create_branch("feature", c1)
        RefManager.create_branch("develop", c1)
        
        branches = RefManager.list_branches()
        assert "main" in branches
        assert "feature" in branches
        assert "develop" in branches
        assert len(branches) >= 3
    
    def test_update_branch(self, sample_commits):
        """Test updating branch pointer."""
        c1 = sample_commits["c1"]
        c2 = sample_commits["c2"]
        
        RefManager.create_branch("test", c1)
        assert RefManager.get_branch_commit("test") == c1
        
        RefManager.update_branch("test", c2)
        assert RefManager.get_branch_commit("test") == c2
    
    def test_delete_branch(self, sample_commits):
        """Test deleting a branch."""
        c1 = sample_commits["c1"]
        RefManager.create_branch("temp", c1)
        assert RefManager.branch_exists("temp")
        
        RefManager.delete_branch("temp")
        assert not RefManager.branch_exists("temp")
    
    def test_cannot_delete_checked_out_branch(self, sample_commits):
        """Test that we can't delete currently checked-out branch."""
        c1 = sample_commits["c1"]
        RefManager.create_branch("feature", c1)
        RefManager.set_head_to_branch("feature")
        
        with pytest.raises(ValueError):
            RefManager.delete_branch("feature")
    
    def test_get_branch_commit(self, sample_commits):
        """Test getting commit from branch."""
        c1 = sample_commits["c1"]
        RefManager.create_branch("test", c1)
        
        commit = RefManager.get_branch_commit("test")
        assert commit == c1
    
    def test_get_nonexistent_branch_commit(self, clean_repo):
        """Test getting commit from nonexistent branch."""
        commit = RefManager.get_branch_commit("nonexistent")
        assert commit is None
    
    def test_get_current_branch(self, sample_commits):
        """Test getting current branch name."""
        RefManager.set_head_to_branch("main")
        branch = RefManager.get_current_branch()
        assert branch == "main"
        
        # Detached HEAD
        RefManager.set_head_detached(sample_commits["c1"])
        branch = RefManager.get_current_branch()
        assert branch is None
    
    def test_get_current_commit(self, sample_commits):
        """Test getting current commit."""
        c2 = sample_commits["c2"]
        RefManager.update_branch("main", c2)
        RefManager.set_head_to_branch("main")
        
        commit = RefManager.get_current_commit()
        assert commit == c2
