"""Tests for SnapGit object storage system."""

import os
import pytest
from snapgit.objects import ObjectStore, create_blob, create_commit


class TestObjectStore:
    """Test ObjectStore functionality."""
    
    def test_write_and_read_blob(self, temp_repo):
        """Test writing and reading blob objects."""
        content = b"Hello, SnapGit!"
        blob_hash = ObjectStore.write_object("blob", content)
        
        assert blob_hash is not None
        assert len(blob_hash) == 40  # SHA1 is 40 chars
        
        obj_type, read_content = ObjectStore.read_object(blob_hash)
        assert obj_type == "blob"
        assert read_content == content
    
    def test_write_and_read_commit(self, temp_repo):
        """Test writing and reading commit objects."""
        content = b"parent abc123\nauthor Test\ndate 1000\nmessage test\nfile.txt hash\n"
        commit_hash = ObjectStore.write_object("commit", content)
        
        obj_type, read_content = ObjectStore.read_object(commit_hash)
        assert obj_type == "commit"
        assert read_content == content
    
    def test_immutability(self, temp_repo):
        """Test that objects are immutable (can't overwrite)."""
        content1 = b"original"
        hash1 = ObjectStore.write_object("blob", content1)
        
        # Try to write different content with same approach (shouldn't overwrite)
        # Since hash is based on content, different content = different hash
        content2 = b"modified"
        hash2 = ObjectStore.write_object("blob", content2)
        
        assert hash1 != hash2
        
        # Verify original still exists
        _, read_content = ObjectStore.read_object(hash1)
        assert read_content == content1
    
    def test_hash_computation(self, temp_repo):
        """Test that same content produces same hash."""
        content = b"test content"
        hash1 = ObjectStore.write_object("blob", content)
        hash2 = ObjectStore.write_object("blob", content)
        
        assert hash1 == hash2
    
    def test_read_nonexistent(self, temp_repo):
        """Test reading nonexistent object raises error."""
        with pytest.raises(FileNotFoundError):
            ObjectStore.read_object("0" * 40)


class TestBlobCreation:
    """Test blob creation helper."""
    
    def test_create_blob(self, temp_repo):
        """Test creating blob objects."""
        content = b"file content"
        blob_hash = create_blob(content)
        
        assert blob_hash is not None
        obj_type, read_content = ObjectStore.read_object(blob_hash)
        assert obj_type == "blob"
        assert read_content == content
    
    def test_create_blob_empty(self, temp_repo):
        """Test creating empty blob."""
        blob_hash = create_blob(b"")
        
        obj_type, content = ObjectStore.read_object(blob_hash)
        assert obj_type == "blob"
        assert content == b""


class TestCommitCreation:
    """Test commit creation helper."""
    
    def test_create_commit_single_parent(self, temp_repo):
        """Test creating commit with single parent."""
        blob = create_blob(b"content")
        commit = create_commit(
            message="test commit",
            parent="parent123",
            tree_data=f"file.txt {blob}\n",
            author="Test Author"
        )
        
        assert commit is not None
        obj_type, content = ObjectStore.read_object(commit)
        assert obj_type == "commit"
        assert b"parent parent123" in content
        assert b"author Test Author" in content
        assert b"test commit" in content
    
    def test_create_commit_no_parent(self, temp_repo):
        """Test creating commit without parent."""
        commit = create_commit(
            message="initial commit",
            parent=None,
            tree_data="",
            author="Test Author"
        )
        
        obj_type, content = ObjectStore.read_object(commit)
        assert obj_type == "commit"
        # Should not have parent line
        assert b"parent" not in content
        assert b"initial commit" in content
    
    def test_create_commit_multiple_parents(self, temp_repo):
        """Test creating commit with multiple parents (merge commit)."""
        commit = create_commit(
            message="merge commit",
            parents=["parent1", "parent2"],
            tree_data="",
            author="Merge Bot"
        )
        
        obj_type, content = ObjectStore.read_object(commit)
        assert obj_type == "commit"
        assert b"parent parent1" in content
        assert b"parent parent2" in content
        assert b"merge commit" in content
    
    def test_create_commit_with_date(self, temp_repo):
        """Test creating commit with specific date."""
        commit = create_commit(
            message="dated commit",
            parent=None,
            tree_data="",
            date="1234567890"
        )
        
        obj_type, content = ObjectStore.read_object(commit)
        assert b"date 1234567890" in content
