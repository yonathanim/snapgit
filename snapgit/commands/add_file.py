"""Add file to SnapGit index (stage for commit)."""

import os
from ..utils import read_file, update_index
from ..objects import create_blob


def add_file(filename: str) -> None:
    """
    Stage a file for commit.
    
    Process:
    1. Verify repository exists
    2. Verify file exists
    3. Create blob object from file content
    4. Add reference to blob in index
    """
    if not os.path.exists(".snapgit"):
        print("Not a SnapGit repository.")
        return

    if not os.path.exists(filename):
        print("File does not exist.")
        return

    # Read file and create blob object
    content = read_file(filename)
    blob_hash = create_blob(content)
    
    # Update index to reference this blob
    update_index(filename, blob_hash)
    
    print(f"Added {filename}")
