"""Check out commits or branches in SnapGit."""

from ..refs import RefManager


def checkout(name: str) -> None:
    """
    Checkout a branch or commit.
    
    - If name is a branch: switch to that branch
    - If name is a commit hash: enter detached HEAD state
    
    Args:
        name: Branch name or commit hash
    """
    # Check if it's a branch
    if RefManager.branch_exists(name):
        RefManager.set_head_to_branch(name)
        commit = RefManager.get_branch_commit(name)
        print(f"Switched to branch '{name}' (commit {commit[:12]})")
    else:
        # Treat as commit hash (detached HEAD)
        RefManager.set_head_detached(name)
        print(f"Detached HEAD at {name[:12]}")
