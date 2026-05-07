"""
SnapGit diff command.

Show differences between commits or versions.

Usage:
    snapgit diff <commit1> <commit2>
    snapgit diff <commit>              # Compare commit with HEAD
"""

from ..graph import CommitGraph
from ..diff import DiffEngine


def diff(commit1: str = None, commit2: str = None) -> None:
    """
    Show diff between two commits.
    
    Args:
        commit1: First commit hash (default: HEAD)
        commit2: Second commit hash (default: working directory)
        
    Raises:
        ValueError: If commits not found
    """
    # Handle default cases
    if commit1 is None:
        # No args: compare HEAD with working directory (future)
        raise ValueError("Currently only supports: snapgit diff <commit1> <commit2>")
    
    if commit2 is None:
        # One arg: compare with HEAD (for now, show as HEAD vs commit)
        commit2 = commit1
        commit1 = None
    
    # Get commits
    if commit1:
        node1 = CommitGraph.parse_commit(commit1)
        if not node1:
            raise ValueError(f"Commit {commit1} not found")
    else:
        # Compare with current HEAD
        from ..refs import RefManager
        head_commit = RefManager.get_current_commit()
        if not head_commit:
            raise ValueError("No commits in repository")
        node1 = CommitGraph.parse_commit(head_commit)
    
    node2 = CommitGraph.parse_commit(commit2)
    if not node2:
        raise ValueError(f"Commit {commit2} not found")
    
    # Generate diff
    diff_output = DiffEngine.diff_trees(node1.tree_data, node2.tree_data)
    
    print(diff_output)
