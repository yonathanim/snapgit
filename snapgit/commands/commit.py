"""Create a commit in the SnapGit repository."""

import os
from ..utils import read_index, get_current_commit, get_head_ref
from ..objects import create_commit as create_commit_object


def create_commit(message: str) -> None:
    """
    Create a commit from staged files.
    
    Process:
    1. Verify there are staged files (index not empty)
    2. Get parent commit (if any)
    3. Build tree data from index
    4. Create commit object via ObjectStore
    5. Update HEAD reference
    6. Clear index
    
    Args:
        message: Commit message
    """
    repo = ".snapgit"
    
    index_entries = read_index()
    
    if not index_entries:
        print("Nothing to commit.")
        return
    
    parent = get_current_commit()
    
    # Build tree data from index entries
    tree_data = "".join(index_entries)
    
    # Create commit object (ObjectStore handles hashing and storage)
    commit_hash = create_commit_object(message, parent, tree_data)
    
    # Update HEAD reference to point to new commit
    ref_path = os.path.join(repo, get_head_ref())
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    
    with open(ref_path, "w") as f:
        f.write(commit_hash)
    
    # Clear index after successful commit
    open(os.path.join(repo, "index"), "w").close()
    
    print(f"Committed: {commit_hash}")
