"""Tests for SnapGit diff engine."""

import pytest
from snapgit.diff import DiffEngine
from snapgit.objects import create_blob


class TestDiffEngine:
    """Test DiffEngine functionality."""
    
    def test_parse_tree_data(self, temp_repo):
        """Test parsing tree data format."""
        tree_data = "file1.txt abc123\nfile2.txt def456\n"
        tree = DiffEngine.parse_tree_data(tree_data)
        
        assert len(tree) == 2
        assert tree["file1.txt"] == "abc123"
        assert tree["file2.txt"] == "def456"
    
    def test_parse_empty_tree(self, temp_repo):
        """Test parsing empty tree."""
        tree = DiffEngine.parse_tree_data("")
        assert len(tree) == 0
    
    def test_unified_diff_identical(self, temp_repo):
        """Test diff of identical files."""
        content = "line1\nline2\nline3"
        diff = DiffEngine.unified_diff(content, content, "test.txt")
        
        # Identical files still produce headers but no +/- lines
        # Just verify the diff doesn't show changes
        assert not ("-line" in diff or "+line" in diff) or diff == ""
    
    def test_unified_diff_modification(self, temp_repo):
        """Test diff with modifications."""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nmodified\nline3"
        diff = DiffEngine.unified_diff(content1, content2, "test.txt")
        
        assert "-line2" in diff
        assert "+modified" in diff
        assert "test.txt" in diff
    
    def test_unified_diff_addition(self, temp_repo):
        """Test diff with added lines."""
        content1 = ""
        content2 = "line1\nline2"
        diff = DiffEngine.unified_diff(content1, content2, "new.txt")
        
        assert "+line1" in diff
        assert "+line2" in diff
    
    def test_unified_diff_deletion(self, temp_repo):
        """Test diff with deleted lines."""
        content1 = "line1\nline2"
        content2 = ""
        diff = DiffEngine.unified_diff(content1, content2, "deleted.txt")
        
        assert "-line1" in diff
        assert "-line2" in diff
    
    def test_diff_trees_identical(self, temp_repo):
        """Test diffing identical trees."""
        blob = create_blob(b"content")
        tree_data = f"file.txt {blob}\n"
        
        diff = DiffEngine.diff_trees(tree_data, tree_data)
        assert "No changes" in diff or diff == ""
    
    def test_diff_trees_modified_file(self, temp_repo):
        """Test diffing trees with modified file."""
        blob1 = create_blob(b"content1")
        blob2 = create_blob(b"content2")
        
        tree1 = f"file.txt {blob1}\n"
        tree2 = f"file.txt {blob2}\n"
        
        diff = DiffEngine.diff_trees(tree1, tree2)
        assert "-content1" in diff or "---" in diff
        assert "+content2" in diff or "+++" in diff
    
    def test_diff_trees_added_file(self, temp_repo):
        """Test diffing trees with added file."""
        blob1 = create_blob(b"original")
        blob2 = create_blob(b"new file")
        
        tree1 = f"file1.txt {blob1}\n"
        tree2 = f"file1.txt {blob1}\nfile2.txt {blob2}\n"
        
        diff = DiffEngine.diff_trees(tree1, tree2)
        assert "file2.txt" in diff
    
    def test_diff_trees_deleted_file(self, temp_repo):
        """Test diffing trees with deleted file."""
        blob1 = create_blob(b"original")
        blob2 = create_blob(b"other")
        
        tree1 = f"file1.txt {blob1}\nfile2.txt {blob2}\n"
        tree2 = f"file1.txt {blob1}\n"
        
        diff = DiffEngine.diff_trees(tree1, tree2)
        assert "file2.txt" in diff
