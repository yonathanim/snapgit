"""
SnapGit Reference Management.

Manages repository references:
- HEAD: Points to current branch or commit
- Branches: refs/heads/<branch-name>
- Refs: General reference system (prepared for future tags, etc.)

Git's HEAD:
- Detached: HEAD contains commit hash directly
- On branch: HEAD contains "ref: refs/heads/<branch>"

This module ensures consistency between HEAD and branch refs.
"""

import os
from typing import Optional, Tuple


class RefManager:
    """Manage repository references and HEAD state."""
    
    REPO_DIR = ".snapgit"
    HEAD_FILE = os.path.join(REPO_DIR, "HEAD")
    REFS_DIR = os.path.join(REPO_DIR, "refs")
    HEADS_DIR = os.path.join(REFS_DIR, "heads")
    
    @staticmethod
    def _ensure_repo() -> None:
        """Ensure .snapgit directory exists."""
        if not os.path.exists(RefManager.REPO_DIR):
            raise RuntimeError("Not a SnapGit repository")
    
    @staticmethod
    def initialize() -> None:
        """Initialize HEAD to point to main branch."""
        RefManager._ensure_repo()
        os.makedirs(RefManager.HEADS_DIR, exist_ok=True)
        RefManager.set_head_to_branch("main")
    
    @staticmethod
    def set_head_to_branch(branch_name: str) -> None:
        """
        Point HEAD to a branch.
        
        Sets: HEAD = "ref: refs/heads/<branch>"
        """
        ref_path = f"refs/heads/{branch_name}"
        with open(RefManager.HEAD_FILE, "w") as f:
            f.write(f"ref: {ref_path}\n")
    
    @staticmethod
    def set_head_detached(commit_hash: str) -> None:
        """
        Point HEAD directly to a commit (detached state).
        
        Sets: HEAD = "<commit-hash>"
        """
        with open(RefManager.HEAD_FILE, "w") as f:
            f.write(commit_hash + "\n")
    
    @staticmethod
    def get_head_ref() -> str:
        """
        Read HEAD file content (raw).
        
        Returns:
            Either "ref: refs/heads/<branch>" or "<commit-hash>"
        """
        with open(RefManager.HEAD_FILE, "r") as f:
            return f.read().strip()
    
    @staticmethod
    def resolve_head() -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve HEAD to actual commit and branch.
        
        Returns:
            (commit_hash, branch_name) tuple
            - If on a branch: both populated
            - If detached: branch_name is None
            - If no commits: commit_hash is None
        """
        head_content = RefManager.get_head_ref()
        
        # Check if symbolic ref
        if head_content.startswith("ref: "):
            # On a branch
            ref_path = head_content[5:]  # Remove "ref: "
            branch_name = ref_path.split("/")[-1]  # Extract branch name
            
            # Read branch ref to get commit
            ref_file = os.path.join(RefManager.REPO_DIR, ref_path)
            if os.path.exists(ref_file):
                with open(ref_file, "r") as f:
                    commit_hash = f.read().strip()
                return commit_hash, branch_name
            else:
                # Branch doesn't have a commit yet
                return None, branch_name
        else:
            # Detached HEAD
            commit_hash = head_content if head_content else None
            return commit_hash, None
    
    @staticmethod
    def get_current_branch() -> Optional[str]:
        """Get current branch name, or None if detached."""
        _, branch = RefManager.resolve_head()
        return branch
    
    @staticmethod
    def get_current_commit() -> Optional[str]:
        """Get current commit hash, or None if no commits."""
        commit, _ = RefManager.resolve_head()
        return commit
    
    @staticmethod
    def create_branch(branch_name: str, commit_hash: str) -> None:
        """
        Create a new branch pointing to a commit.
        
        Args:
            branch_name: Name of branch (e.g., "develop")
            commit_hash: Commit to point to
            
        Raises:
            ValueError: If branch already exists
        """
        branch_file = os.path.join(RefManager.HEADS_DIR, branch_name)
        
        if os.path.exists(branch_file):
            raise ValueError(f"Branch '{branch_name}' already exists")
        
        os.makedirs(os.path.dirname(branch_file), exist_ok=True)
        with open(branch_file, "w") as f:
            f.write(commit_hash + "\n")
    
    @staticmethod
    def update_branch(branch_name: str, commit_hash: str) -> None:
        """Update an existing branch to point to a commit."""
        branch_file = os.path.join(RefManager.HEADS_DIR, branch_name)
        with open(branch_file, "w") as f:
            f.write(commit_hash + "\n")
    
    @staticmethod
    def get_branch_commit(branch_name: str) -> Optional[str]:
        """Get the commit a branch points to."""
        branch_file = os.path.join(RefManager.HEADS_DIR, branch_name)
        if not os.path.exists(branch_file):
            return None
        with open(branch_file, "r") as f:
            return f.read().strip()
    
    @staticmethod
    def list_branches() -> list:
        """List all branches."""
        if not os.path.exists(RefManager.HEADS_DIR):
            return []
        
        branches = []
        for name in os.listdir(RefManager.HEADS_DIR):
            path = os.path.join(RefManager.HEADS_DIR, name)
            if os.path.isfile(path):
                branches.append(name)
        
        return sorted(branches)
    
    @staticmethod
    def branch_exists(branch_name: str) -> bool:
        """Check if a branch exists."""
        branch_file = os.path.join(RefManager.HEADS_DIR, branch_name)
        return os.path.exists(branch_file)
    
    @staticmethod
    def delete_branch(branch_name: str) -> None:
        """Delete a branch (with safety checks)."""
        current_branch = RefManager.get_current_branch()
        if current_branch == branch_name:
            raise ValueError(f"Cannot delete currently checked-out branch '{branch_name}'")
        
        branch_file = os.path.join(RefManager.HEADS_DIR, branch_name)
        if os.path.exists(branch_file):
            os.remove(branch_file)
