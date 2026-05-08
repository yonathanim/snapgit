"""Tests for SnapGit commit graph."""

import pytest
from snapgit.graph import CommitGraph
from snapgit.objects import create_commit


class TestCommitGraph:
    """Test CommitGraph functionality."""
    
    def test_parse_commit(self, sample_commits):
        """Test parsing commit objects."""
        c1 = sample_commits["c1"]
        node = CommitGraph.parse_commit(c1)
        
        assert node is not None
        assert node.hash == c1
        assert node.message == "first commit"
        assert node.author == "Test Author"
        assert len(node.parents) == 0
    
    def test_parse_commit_with_parent(self, sample_commits):
        """Test parsing commit with parent."""
        c2 = sample_commits["c2"]
        node = CommitGraph.parse_commit(c2)
        
        assert node is not None
        assert node.message == "second commit"
        assert len(node.parents) == 1
        assert node.parents[0] == sample_commits["c1"]
    
    def test_parse_nonexistent_commit(self, temp_repo):
        """Test parsing nonexistent commit returns None."""
        node = CommitGraph.parse_commit("0" * 40)
        assert node is None
    
    def test_get_history_linear(self, sample_commits):
        """Test getting linear history."""
        c3 = sample_commits["c3"]
        history = CommitGraph.get_history(c3)
        
        assert len(history) == 3
        assert history[0].hash == c3
        assert history[1].hash == sample_commits["c2"]
        assert history[2].hash == sample_commits["c1"]
    
    def test_get_history_max_count(self, sample_commits):
        """Test limiting history with max_count."""
        c3 = sample_commits["c3"]
        history = CommitGraph.get_history(c3, max_count=2)
        
        assert len(history) == 2
        assert history[0].hash == c3
        assert history[1].hash == sample_commits["c2"]
    
    def test_get_merge_base_same_commit(self, sample_commits):
        """Test merge base of commit with itself."""
        c2 = sample_commits["c2"]
        merge_base = CommitGraph.get_merge_base(c2, c2)
        
        assert merge_base == c2
    
    def test_get_merge_base_linear(self, sample_commits):
        """Test merge base in linear history."""
        c2 = sample_commits["c2"]
        c3 = sample_commits["c3"]
        merge_base = CommitGraph.get_merge_base(c2, c3)
        
        assert merge_base == c2
    
    def test_get_merge_base_branched(self, branched_repo):
        """Test merge base with branched history."""
        c3 = branched_repo["c3"]
        c_feature = branched_repo["c_feature"]
        c1 = branched_repo["c1"]
        
        merge_base = CommitGraph.get_merge_base(c3, c_feature)
        assert merge_base == c1
    
    def test_is_ancestor_true(self, sample_commits):
        """Test ancestor check returns true."""
        c1 = sample_commits["c1"]
        c3 = sample_commits["c3"]
        
        assert CommitGraph.is_ancestor(c1, c3)
    
    def test_is_ancestor_false(self, sample_commits):
        """Test ancestor check returns false."""
        c2 = sample_commits["c2"]
        c1 = sample_commits["c1"]
        
        assert not CommitGraph.is_ancestor(c2, c1)
    
    def test_is_ancestor_self(self, sample_commits):
        """Test that commit is ancestor of itself."""
        c1 = sample_commits["c1"]
        assert CommitGraph.is_ancestor(c1, c1)
    
    def test_format_log_single_commit(self, clean_repo):
        """Test formatting log with single commit."""
        from snapgit.refs import RefManager
        commit = create_commit(
            message="test",
            parent=None,
            tree_data="",
            author="Author"
        )
        RefManager.update_branch("main", commit)
        
        log_output = CommitGraph.format_log(commit)
        assert "test" in log_output
        assert "Author" in log_output
    
    def test_format_log_multiple_commits(self, sample_commits):
        """Test formatting log with multiple commits."""
        c3 = sample_commits["c3"]
        log_output = CommitGraph.format_log(c3)
        
        assert "first commit" in log_output
        assert "second commit" in log_output
        assert "third commit" in log_output
    
    def test_format_log_with_branch(self, sample_commits):
        """Test that log shows branch decorations."""
        c3 = sample_commits["c3"]
        from snapgit.refs import RefManager
        RefManager.set_head_to_branch("main")
        
        log_output = CommitGraph.format_log(c3)
        assert "(main)" in log_output
