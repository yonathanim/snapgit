"""
SnapGit merge command.

Merge one branch into the current branch.

Usage:
    snapgit merge <branch>
"""

from ..refs import RefManager
from ..graph import CommitGraph
from ..merge import MergeOrchestrator
from ..objects import create_commit


def merge(branch_name: str) -> None:
    """
    Merge a branch into the current branch.
    
    Args:
        branch_name: Name of branch to merge
        
    Raises:
        ValueError: If branch doesn't exist, is the same as current, or merge fails
    """
    # Get current branch info
    current_commit, current_branch = RefManager.resolve_head()
    
    if current_branch is None:
        raise ValueError("Cannot merge while in detached HEAD state")
    
    if current_commit is None:
        raise ValueError("Current branch has no commits yet")
    
    # Get target branch
    if not RefManager.branch_exists(branch_name):
        raise ValueError(f"Branch '{branch_name}' does not exist")
    
    if current_branch == branch_name:
        raise ValueError("Cannot merge a branch into itself")
    
    target_commit = RefManager.get_branch_commit(branch_name)
    if target_commit is None:
        raise ValueError(f"Branch '{branch_name}' has no commits")
    
    # Check if already merged (fast-forward or already ancestor)
    if CommitGraph.is_ancestor(target_commit, current_commit):
        print(f"Already up to date: {current_branch} contains all commits from {branch_name}")
        return
    
    # Check for fast-forward (target is ahead of current)
    if CommitGraph.is_ancestor(current_commit, target_commit):
        # Fast-forward merge
        RefManager.update_branch(current_branch, target_commit)
        print(f"Fast-forward merge: {current_branch} -> {target_commit[:12]}")
        return
    
    # Perform three-way merge
    success, merged_tree, conflict_files = MergeOrchestrator.merge_branches(
        current_commit=current_commit,
        target_commit=target_commit,
        current_branch=current_branch,
        target_branch=branch_name
    )
    
    if not success:
        # Conflicts exist
        print(f"Merge conflict in {len(conflict_files)} file(s):")
        for filename in conflict_files:
            print(f"  {filename}")
        print("\nResolve conflicts and commit manually.")
        raise ValueError("Merge failed due to conflicts")
    
    # Create merge commit
    merge_message = f"Merge branch '{branch_name}' into '{current_branch}'"
    merge_commit = create_commit(
        message=merge_message,
        parents=[current_commit, target_commit],
        tree_data=merged_tree,
        author="SnapGit Merge",
        date=None
    )
    
    # Update branch
    RefManager.update_branch(current_branch, merge_commit)
    
    print(f"Merge successful: created commit {merge_commit[:12]}")
    print(f"  Merge branch '{branch_name}' into '{current_branch}'")
    print(f"  Parents: {current_commit[:12]}, {target_commit[:12]}")
