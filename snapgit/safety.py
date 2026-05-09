"""SnapGit Safety and Validation Systems.

Protects repository integrity by validating all operations.

Implements:
- Hash validation (SHA1 format)
- Branch name validation
- Commit validation
- Reference integrity checks
- Dirty working tree detection
- Safe operations with rollback
"""

import os
import re
from typing import List, Tuple, Optional


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class SafetyValidator:
    """Centralized validation for repository safety."""
    
    @staticmethod
    def validate_hash(hash_value: str) -> bool:
        """Validate commit/object hash format (40-char hex SHA1)."""
        if not hash_value:
            return False
        if len(hash_value) != 40:
            return False
        if not all(c in "0123456789abcdef" for c in hash_value):
            return False
        return True
    
    @staticmethod
    def validate_branch_name(name: str) -> bool:
        """Validate branch name (no spaces, special chars, or ..)."""
        if not name:
            return False
        # Git-like validation: alphanumeric, _, -, ., no leading/trailing special chars
        if name.startswith("-") or name.startswith("."):
            return False
        if name.endswith("."):
            return False
        if ".." in name:  # Prevent double dots
            return False
        # Allow alphanumeric, underscore, hyphen, dot, forward slash
        if not re.match(r'^[a-zA-Z0-9_\-./]+$', name):
            return False
        return True
    
    @staticmethod
    def validate_commit_hash(commit_hash: str) -> bool:
        """Validate commit hash and ensure it exists."""
        if not SafetyValidator.validate_hash(commit_hash):
            raise ValidationError(f"Invalid commit hash format: {commit_hash}")
        
        # Check if commit object actually exists
        from .objects import ObjectStore
        try:
            obj_type, _ = ObjectStore.read_object(commit_hash)
            if obj_type != "commit":
                raise ValidationError(f"Object is not a commit: {commit_hash}")
        except FileNotFoundError:
            raise ValidationError(f"Commit not found: {commit_hash}")
        
        return True
    
    @staticmethod
    def validate_branch_exists(branch_name: str) -> bool:
        """Validate branch exists and has a valid commit."""
        from .refs import RefManager
        
        if not SafetyValidator.validate_branch_name(branch_name):
            raise ValidationError(f"Invalid branch name: {branch_name}")
        
        if not RefManager.branch_exists(branch_name):
            raise ValidationError(f"Branch does not exist: {branch_name}")
        
        commit = RefManager.get_branch_commit(branch_name)
        if commit is None:
            raise ValidationError(f"Branch has no commits: {branch_name}")
        
        return True
    
    @staticmethod
    def validate_target_for_checkout(target: str) -> bool:
        """Validate target is valid for checkout (branch or commit)."""
        from .refs import RefManager
        
        # Check if it's a branch
        if RefManager.branch_exists(target):
            return True
        
        # Check if it's a valid commit hash
        if SafetyValidator.validate_hash(target):
            try:
                SafetyValidator.validate_commit_hash(target)
                return True
            except ValidationError:
                pass
        
        raise ValidationError(f"Invalid checkout target: {target}")
    
    @staticmethod
    def validate_merge_preconditions(target_branch: str) -> bool:
        """Validate merge operation is safe."""
        from .refs import RefManager
        from .graph import CommitGraph
        
        # Validate branch exists
        SafetyValidator.validate_branch_exists(target_branch)
        
        # Get current branch
        current_commit, current_branch = RefManager.resolve_head()
        
        # Check we're not in detached HEAD state
        if current_branch is None:
            raise ValidationError("Cannot merge while in detached HEAD state")
        
        # Check not merging into self
        if current_branch == target_branch:
            raise ValidationError(f"Cannot merge branch into itself: {target_branch}")
        
        # Get target commit
        target_commit = RefManager.get_branch_commit(target_branch)
        
        # Check they have a common ancestor
        merge_base = CommitGraph.get_merge_base(current_commit, target_commit)
        if merge_base is None:
            raise ValidationError(
                f"No common ancestor between {current_branch} and {target_branch}"
            )
        
        return True
    
    @staticmethod
    def detect_dirty_tree() -> bool:
        """Detect if working directory has uncommitted changes."""
        from .refs import RefManager
        from .objects import ObjectStore
        
        current_commit, _ = RefManager.resolve_head()
        if current_commit is None:
            # No commits yet - check if there are staged files
            index_path = ".snapgit/index"
            return os.path.exists(index_path) and os.path.getsize(index_path) > 0
        
        # Get HEAD tree
        try:
            obj_type, content = ObjectStore.read_object(current_commit)
            if obj_type != "commit":
                raise ValidationError(f"HEAD does not point to commit: {current_commit}")
            
            # Parse commit to get tree
            lines = content.decode().split("\n")
            head_tree_data = ""
            for line in lines:
                if line and not line.startswith("parent ") and \
                   not line.startswith("author ") and \
                   not line.startswith("date ") and \
                   not line.startswith("message "):
                    head_tree_data += line + "\n"
            
            # Check if index exists and differs from HEAD
            index_path = ".snapgit/index"
            if os.path.exists(index_path):
                with open(index_path, "rb") as f:
                    index_content = f.read().decode()
                if index_content.strip() != head_tree_data.strip():
                    return True
            
            return False
        except FileNotFoundError:
            return False
    
    @staticmethod
    def check_repository_initialized() -> bool:
        """Check if .snapgit directory exists."""
        if not os.path.exists(".snapgit"):
            raise ValidationError(
                "Not a SnapGit repository. Use 'snapgit init' to initialize."
            )
        
        required_dirs = [".snapgit", ".snapgit/objects", ".snapgit/refs/heads"]
        for required_dir in required_dirs:
            if not os.path.exists(required_dir):
                raise ValidationError(
                    f"Corrupted repository: missing {required_dir}. "
                    f"Consider re-initializing the repository."
                )
        
        return True
    
    @staticmethod
    def validate_ref_integrity() -> List[str]:
        """Validate all refs point to valid commits. Returns list of problems."""
        from .refs import RefManager
        from .objects import ObjectStore
        
        problems = []
        
        try:
            branches = RefManager.list_branches()
        except Exception as e:
            return [f"Failed to list branches: {e}"]
        
        for branch in branches:
            try:
                commit = RefManager.get_branch_commit(branch)
                if commit is None:
                    problems.append(f"Branch '{branch}' has no commits")
                elif not SafetyValidator.validate_hash(commit):
                    problems.append(f"Branch '{branch}' has invalid commit hash: {commit}")
                else:
                    try:
                        obj_type, _ = ObjectStore.read_object(commit)
                        if obj_type != "commit":
                            problems.append(f"Branch '{branch}' points to non-commit: {commit}")
                    except FileNotFoundError:
                        problems.append(f"Branch '{branch}' points to missing commit: {commit}")
            except Exception as e:
                problems.append(f"Error checking branch '{branch}': {e}")
        
        return problems
    
    @staticmethod
    def validate_commit_parents(commit_hash: str) -> bool:
        """Validate commit's parent references are valid."""
        from .objects import ObjectStore
        from .graph import CommitGraph
        
        SafetyValidator.validate_commit_hash(commit_hash)
        
        try:
            node = CommitGraph.parse_commit(commit_hash)
            if node is None:
                raise ValidationError(f"Cannot parse commit: {commit_hash}")
            
            for parent in node.parents:
                if not SafetyValidator.validate_hash(parent):
                    raise ValidationError(
                        f"Commit {commit_hash} has invalid parent: {parent}"
                    )
                try:
                    obj_type, _ = ObjectStore.read_object(parent)
                    if obj_type != "commit":
                        raise ValidationError(
                            f"Parent {parent} is not a commit"
                        )
                except FileNotFoundError:
                    raise ValidationError(
                        f"Parent {parent} not found (repository may be corrupted)"
                    )
            
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error validating commit: {e}")
