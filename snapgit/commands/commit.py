"""Create a commit in the SnapGit repository."""

import os
from ..utils import read_index
from ..refs import RefManager
from ..objects import create_commit as create_commit_object


def create_commit(message: str, author: str = "SnapGit User") -> None:
    """
    Create a commit from staged files.
    
    Process:
    1. Verify there are staged files (index not empty)
    2. Get parent commit (if any)
    3. Build tree data from index
    4. Create commit object via ObjectStore (with author/date metadata)
    5. Update current branch pointer
    6. Clear index
    
    Args:
        message: Commit message
        author: Author name (default: "SnapGit User")
    """
    repo = ".snapgit"
    
    index_entries = read_index()
    
    if not index_entries:
        print("Nothing to commit.")
        return
    
    # Get current commit (if any)
    parent = RefManager.get_current_commit()
    
    # Build tree data from index entries
    tree_data = "".join(index_entries)
    
    # Create commit object (includes author, date metadata)
    commit_hash = create_commit_object(message, parent, tree_data, author=author)
    
    # Update current branch to point to new commit
    current_branch = RefManager.get_current_branch()
    if current_branch:
        RefManager.update_branch(current_branch, commit_hash)
    else:
        # Detached HEAD - update HEAD directly
        RefManager.set_head_detached(commit_hash)
    
    # Clear index after successful commit
    open(os.path.join(repo, "index"), "w").close()
    
    print(f"Committed: {commit_hash}")
