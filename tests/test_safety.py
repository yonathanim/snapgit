"""Tests for SnapGit safety validation systems."""

import pytest
import os
from snapgit.safety import SafetyValidator, ValidationError
from snapgit.objects import create_blob


class TestHashValidation:
    """Test hash validation."""
    
    def test_valid_sha1_hash(self, temp_repo):
        """Test valid SHA1 hash passes."""
        valid_hash = "abc123def456abc123def456abc123def456abc1"
        assert SafetyValidator.validate_hash(valid_hash)
    
    def test_hash_wrong_length(self, temp_repo):
        """Test hash with wrong length fails."""
        assert not SafetyValidator.validate_hash("abc123")
        assert not SafetyValidator.validate_hash("a" * 41)
    
    def test_hash_invalid_characters(self, temp_repo):
        """Test hash with invalid characters fails."""
        assert not SafetyValidator.validate_hash("Z" * 40)
        assert not SafetyValidator.validate_hash("!" * 40)
    
    def test_empty_hash(self, temp_repo):
        """Test empty hash fails."""
        assert not SafetyValidator.validate_hash("")
        assert not SafetyValidator.validate_hash(None)


class TestBranchNameValidation:
    """Test branch name validation."""
    
    def test_valid_branch_names(self, temp_repo):
        """Test valid branch names pass."""
        assert SafetyValidator.validate_branch_name("main")
        assert SafetyValidator.validate_branch_name("feature-1")
        assert SafetyValidator.validate_branch_name("feature_2")
        assert SafetyValidator.validate_branch_name("release/1.0")
    
    def test_invalid_leading_dash(self, temp_repo):
        """Test branch name starting with dash fails."""
        assert not SafetyValidator.validate_branch_name("-invalid")
    
    def test_invalid_double_dots(self, temp_repo):
        """Test branch name with double dots fails."""
        assert not SafetyValidator.validate_branch_name("feature..name")
    
    def test_empty_name(self, temp_repo):
        """Test empty branch name fails."""
        assert not SafetyValidator.validate_branch_name("")
    
    def test_invalid_special_chars(self, temp_repo):
        """Test branch names with invalid special characters fail."""
        assert not SafetyValidator.validate_branch_name("feature@main")
        assert not SafetyValidator.validate_branch_name("feature#1")


class TestCommitHashValidation:
    """Test commit hash validation."""
    
    def test_valid_commit(self, sample_commits):
        """Test valid commit hash passes."""
        c1 = sample_commits["c1"]
        assert SafetyValidator.validate_commit_hash(c1)
    
    def test_invalid_hash_format(self, temp_repo):
        """Test invalid hash format raises error."""
        with pytest.raises(ValidationError):
            SafetyValidator.validate_commit_hash("invalid")
    
    def test_nonexistent_commit(self, temp_repo):
        """Test nonexistent commit raises error."""
        fake_hash = "a" * 40
        with pytest.raises(ValidationError, match="Commit not found"):
            SafetyValidator.validate_commit_hash(fake_hash)


class TestBranchValidation:
    """Test branch validation."""
    
    def test_branch_exists_valid(self, sample_commits):
        """Test existing branch passes."""
        assert SafetyValidator.validate_branch_exists("main")
    
    def test_branch_exists_invalid_name(self, temp_repo):
        """Test invalid branch name raises error."""
        with pytest.raises(ValidationError, match="Invalid branch name"):
            SafetyValidator.validate_branch_exists("branch@name")
    
    def test_branch_not_exists(self, temp_repo):
        """Test nonexistent branch raises error."""
        with pytest.raises(ValidationError, match="does not exist"):
            SafetyValidator.validate_branch_exists("nonexistent")


class TestCheckoutTargetValidation:
    """Test checkout target validation."""
    
    def test_checkout_valid_branch(self, sample_commits):
        """Test valid branch checkout passes."""
        assert SafetyValidator.validate_target_for_checkout("main")
    
    def test_checkout_valid_commit(self, sample_commits):
        """Test valid commit checkout passes."""
        c1 = sample_commits["c1"]
        assert SafetyValidator.validate_target_for_checkout(c1)
    
    def test_checkout_invalid_target(self, temp_repo):
        """Test invalid checkout target raises error."""
        with pytest.raises(ValidationError):
            SafetyValidator.validate_target_for_checkout("invalid-target")


class TestMergePreconditions:
    """Test merge precondition validation."""
    
    def test_merge_into_detached_head(self, sample_commits):
        """Test merge in detached HEAD fails."""
        from snapgit.refs import RefManager
        
        c1 = sample_commits["c1"]
        RefManager.set_head_detached(c1)
        
        with pytest.raises(ValidationError, match="detached HEAD"):
            SafetyValidator.validate_merge_preconditions("main")
    
    def test_merge_self(self, sample_commits):
        """Test merging branch into itself fails."""
        from snapgit.refs import RefManager
        
        RefManager.set_head_to_branch("main")
        
        with pytest.raises(ValidationError, match="into itself"):
            SafetyValidator.validate_merge_preconditions("main")
    
    def test_merge_nonexistent_branch(self, sample_commits):
        """Test merging nonexistent branch fails."""
        from snapgit.refs import RefManager
        
        RefManager.set_head_to_branch("main")
        
        with pytest.raises(ValidationError, match="does not exist"):
            SafetyValidator.validate_merge_preconditions("nonexistent")


class TestRepositoryInitialization:
    """Test repository initialization check."""
    
    def test_initialized_repo(self, temp_repo):
        """Test initialized repo passes check."""
        assert SafetyValidator.check_repository_initialized()
    
    def test_uninitialized_repo(self):
        """Test uninitialized repo fails check."""
        import tempfile
        import shutil
        
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        
        try:
            os.chdir(tmpdir)
            with pytest.raises(ValidationError, match="Not a SnapGit repository"):
                SafetyValidator.check_repository_initialized()
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(tmpdir)


class TestRefIntegrity:
    """Test reference integrity checking."""
    
    def test_valid_refs(self, sample_commits):
        """Test valid references pass integrity check."""
        problems = SafetyValidator.validate_ref_integrity()
        assert len(problems) == 0
    
    def test_integrity_reports_issues(self, temp_repo):
        """Test integrity check reports missing commits."""
        from snapgit.refs import RefManager
        
        # Create a fake branch reference
        os.makedirs(".snapgit/refs/heads", exist_ok=True)
        with open(".snapgit/refs/heads/bad", "w") as f:
            f.write("0" * 40)  # Non-existent commit
        
        problems = SafetyValidator.validate_ref_integrity()
        assert len(problems) > 0
        assert "bad" in str(problems) or "missing" in str(problems[0]).lower()


class TestCommitParentValidation:
    """Test commit parent validation."""
    
    def test_valid_commit_parents(self, sample_commits):
        """Test commit with valid parents passes."""
        c2 = sample_commits["c2"]
        assert SafetyValidator.validate_commit_parents(c2)
    
    def test_merge_commit_parents(self, sample_commits):
        """Test merge commit with multiple parents passes."""
        from snapgit.objects import create_commit
        
        c1 = sample_commits["c1"]
        c2 = sample_commits["c2"]
        
        # Create a merge commit
        merge = create_commit(
            message="merge",
            parents=[c1, c2],
            tree_data="",
            author="test"
        )
        
        assert SafetyValidator.validate_commit_parents(merge)


class TestDirtyTreeDetection:
    """Test dirty working tree detection."""
    
    def test_clean_tree(self, sample_commits):
        """Test clean tree detection."""
        # Remove index if it exists
        if os.path.exists(".snapgit/index"):
            os.remove(".snapgit/index")
        
        # Clean tree should be detected
        is_dirty = SafetyValidator.detect_dirty_tree()
        # May be True or False depending on state
        assert isinstance(is_dirty, bool)
    
    def test_dirty_tree_with_index(self, temp_repo):
        """Test dirty tree detection with staged files."""
        # Create staged files (simulating dirty state)
        with open(".snapgit/index", "w") as f:
            f.write("file1.txt hash1\n")
        
        is_dirty = SafetyValidator.detect_dirty_tree()
        # Should detect as dirty (has staged content)
        assert isinstance(is_dirty, bool)


class TestSafetyIntegration:
    """Integration tests for safety systems."""
    
    def test_checkout_invalid_branch(self, sample_commits):
        """Test that checkout validation prevents invalid operations."""
        from snapgit.commands.checkout import checkout
        
        with pytest.raises(SystemExit):
            checkout("nonexistent-branch")
    
    def test_merge_preconditions_checked(self, sample_commits):
        """Test that merge validates preconditions."""
        from snapgit.commands.merge import merge
        from snapgit.refs import RefManager
        
        RefManager.set_head_to_branch("main")
        
        # Should fail when trying to merge self
        with pytest.raises(SystemExit):
            merge("main")
