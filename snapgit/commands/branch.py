"""Manage branches in SnapGit."""

from ..refs import RefManager


def create_branch(name: str) -> None:
    """
    Create a new branch.
    
    Branch points to the current commit and can be switched to later.
    
    Args:
        name: Branch name
    """
    current_commit = RefManager.get_current_commit()
    
    if not current_commit:
        print("Error: no commits available to branch from")
        return
    
    try:
        RefManager.create_branch(name, current_commit)
        print(f"Branch '{name}' created at {current_commit[:12]}")
    except ValueError as e:
        print(f"Error: {e}")


def delete_branch(name: str) -> None:
    """
    Delete a branch.
    
    Cannot delete the currently checked-out branch.
    
    Args:
        name: Branch name
    """
    try:
        RefManager.delete_branch(name)
        print(f"Deleted branch '{name}'")
    except ValueError as e:
        print(f"Error: {e}")


def list_branches() -> None:
    """List all branches, marking current branch with *."""
    current_branch = RefManager.get_current_branch()
    branches = RefManager.list_branches()
    
    for branch in branches:
        marker = "* " if branch == current_branch else "  "
        print(f"{marker}{branch}")


def merge_branch(name: str) -> None:
    """
    Merge a branch into the current branch (placeholder).
    
    Full merge implementation deferred to Phase 4.
    
    Args:
        name: Branch to merge
    """
    branch_commit = RefManager.get_branch_commit(name)
    current_commit = RefManager.get_current_commit()
    
    if not branch_commit:
        print(f"Error: branch '{name}' does not exist")
        return
    
    if branch_commit == current_commit:
        print("Error: branch is already up to date")
        return
    
    print(f"Merge of '{name}' (Phase 3 placeholder)")
    print("Full merge support coming in Phase 4")
