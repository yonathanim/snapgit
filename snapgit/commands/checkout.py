import os
from ..utils import get_head_ref


def checkout(name):
    # Check if it's a branch
    branch_path = os.path.join(".snapgit", "refs", "heads", name)

    if os.path.exists(branch_path):
        # Switch HEAD to branch
        with open(os.path.join(".snapgit", "HEAD"), "w") as f:
            f.write(f"ref: refs/heads/{name}\n")

        with open(branch_path, "r") as f:
            commit_hash = f.read().strip()

        print(f"Switched to branch '{name}'")

    else:
        # Treat as commit hash
        commit_hash = name
        print(f"Detached HEAD at {commit_hash}")

    # Restore files (reuse logic)
    checkout_commit(commit_hash)
