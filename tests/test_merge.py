"""Tests for SnapGit merge engine."""

import pytest
from snapgit.merge import MergeEngine, ConflictMarker
from snapgit.objects import create_blob


class TestConflictMarker:
    """Test ConflictMarker functionality."""
    
    def test_format_marker(self, temp_repo):
        """Test formatting conflict marker."""
        marker = ConflictMarker("file.txt", "ours content", "theirs content")
        formatted = marker.format_marker("OURS", "THEIRS")
        
        assert "<<<<<<" in formatted
        assert "======" in formatted
        assert ">>>>>>" in formatted
        assert "OURS" in formatted
        assert "THEIRS" in formatted


class TestMergeEngine:
    """Test MergeEngine functionality."""
    
    def test_merge_identical_trees(self, temp_repo):
        """Test merging identical trees (no conflict)."""
        blob = create_blob(b"content")
        tree_data = f"file.txt {blob}\n"
        
        result = MergeEngine.merge(tree_data, tree_data, tree_data)
        
        assert result.success
        assert len(result.conflicts) == 0
        assert result.merged_tree == tree_data
    
    def test_merge_no_conflict_ours_modified(self, temp_repo):
        """Test clean merge when only ours changes."""
        blob1 = create_blob(b"base")
        blob2 = create_blob(b"ours")
        blob3 = create_blob(b"base")
        
        base_tree = f"file.txt {blob1}\n"
        ours_tree = f"file.txt {blob2}\n"
        theirs_tree = f"file.txt {blob3}\n"
        
        result = MergeEngine.merge(base_tree, ours_tree, theirs_tree)
        
        assert result.success
        assert len(result.conflicts) == 0
        assert blob2 in result.merged_tree
    
    def test_merge_no_conflict_theirs_modified(self, temp_repo):
        """Test clean merge when only theirs changes."""
        blob1 = create_blob(b"base")
        blob2 = create_blob(b"base")
        blob3 = create_blob(b"theirs")
        
        base_tree = f"file.txt {blob1}\n"
        ours_tree = f"file.txt {blob2}\n"
        theirs_tree = f"file.txt {blob3}\n"
        
        result = MergeEngine.merge(base_tree, ours_tree, theirs_tree)
        
        assert result.success
        assert len(result.conflicts) == 0
        assert blob3 in result.merged_tree
    
    def test_merge_conflict_both_modified(self, temp_repo):
        """Test merge conflict when both sides modify."""
        blob1 = create_blob(b"base")
        blob2 = create_blob(b"ours content")
        blob3 = create_blob(b"theirs content")
        
        base_tree = f"file.txt {blob1}\n"
        ours_tree = f"file.txt {blob2}\n"
        theirs_tree = f"file.txt {blob3}\n"
        
        result = MergeEngine.merge(base_tree, ours_tree, theirs_tree)
        
        # Merge might still succeed but mark conflict
        assert len(result.conflicts) >= 1
        conflict = result.conflicts[0]
        assert conflict.filename == "file.txt"
    
    def test_merge_added_files_both_sides(self, temp_repo):
        """Test merge with added files on both sides."""
        blob1 = create_blob(b"ours new")
        blob2 = create_blob(b"theirs new")
        
        base_tree = ""
        ours_tree = f"new1.txt {blob1}\n"
        theirs_tree = f"new2.txt {blob2}\n"
        
        result = MergeEngine.merge(base_tree, ours_tree, theirs_tree)
        
        # No conflict - different files
        assert result.success
        assert blob1 in result.merged_tree
        assert blob2 in result.merged_tree
    
    def test_merge_removed_added(self, temp_repo):
        """Test merge with file removed on one side, modified on other."""
        blob1 = create_blob(b"original")
        blob2 = create_blob(b"modified")
        
        base_tree = f"file.txt {blob1}\n"
        ours_tree = ""  # We removed it
        theirs_tree = f"file.txt {blob2}\n"  # They modified it
        
        result = MergeEngine.merge(base_tree, ours_tree, theirs_tree)
        
        # This creates a conflict
        assert len(result.conflicts) >= 1
    
    def test_merge_with_labels(self, temp_repo):
        """Test merge with conflict labels."""
        blob1 = create_blob(b"base")
        blob2 = create_blob(b"branch1")
        blob3 = create_blob(b"branch2")
        
        base_tree = f"file.txt {blob1}\n"
        ours_tree = f"file.txt {blob2}\n"
        theirs_tree = f"file.txt {blob3}\n"
        
        result = MergeEngine.merge(
            base_tree, ours_tree, theirs_tree,
            ours_label="main",
            theirs_label="feature"
        )
        
        if result.conflicts:
            conflict = result.conflicts[0]
            formatted = conflict.format_marker("main", "feature")
            assert "main" in formatted
            assert "feature" in formatted
    
    def test_merge_empty_trees(self, temp_repo):
        """Test merging empty trees."""
        result = MergeEngine.merge("", "", "")
        
        assert result.success
        assert len(result.conflicts) == 0
        assert result.merged_tree == ""


class TestMergeOrchestrator:
    """Test high-level merge operations."""
    
    def test_merge_orchestrator_fast_forward(self, sample_commits):
        """Test merge orchestrator detecting fast-forward."""
        from snapgit.merge import MergeOrchestrator
        from snapgit.refs import RefManager
        from snapgit.graph import CommitGraph
        
        c1 = sample_commits["c1"]
        c2 = sample_commits["c2"]
        
        RefManager.update_branch("main", c1)
        RefManager.set_head_to_branch("main")
        RefManager.create_branch("feature", c2)
        
        # Call with correct signature: current_commit, target_commit, current_branch, target_branch
        success, merged_tree, conflicts = MergeOrchestrator.merge_branches(
            c1, c2, "main", "feature"
        )
        
        # Should be fast-forward since c2 is descendant of c1
        assert success
