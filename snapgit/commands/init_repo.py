"""Initialize a new SnapGit repository."""

import os


def init_repo():
    """
    Initialize a new SnapGit repository.
    
    Creates:
    - .snapgit/objects/ (object store)
    - .snapgit/refs/heads/ (branch pointers)
    - .snapgit/HEAD (symbolic reference)
    - .snapgit/index (staging area)
    """
    repo_name = ".snapgit"

    if os.path.exists(repo_name):
        print("Repository already initialized.")
        return

    os.mkdir(repo_name)
    os.mkdir(os.path.join(repo_name, "objects"))
    os.mkdir(os.path.join(repo_name, "refs"))
    os.mkdir(os.path.join(repo_name, "refs", "heads"))

    # Initialize HEAD to point to main branch
    with open(os.path.join(repo_name, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main\n")

    print("Initialized empty SnapGit repository.")
