"""Check out commits or branches in SnapGit."""

from ..refs import RefManager
from ..safety import SafetyValidator, ValidationError
import sys


def checkout(name: str) -> None:
    """
    Checkout a branch or commit.
    
    - If name is a branch: switch to that branch
    - If name is a commit hash: enter detached HEAD state
    
    Args:
        name: Branch name or commit hash
    """
    try:
        SafetyValidator.check_repository_initialized()
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Validate the target
        SafetyValidator.validate_target_for_checkout(name)
        
        # Check if it's a branch
        if RefManager.branch_exists(name):
            RefManager.set_head_to_branch(name)
            commit = RefManager.get_branch_commit(name)
            print(f"Switched to branch '{name}' (commit {commit[:12]})")
        else:
            # Treat as commit hash (detached HEAD)
            RefManager.set_head_detached(name)
            print(f"Detached HEAD at {name[:12]}")
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
