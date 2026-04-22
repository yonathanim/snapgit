import os
from ..utils import get_current_commit


def create_branch(name):
    branch_path = os.path.join(".snapgit", "refs", "heads", name)

    if os.path.exists(branch_path):
        print("Branch already exists")
        return

    current_commit = get_current_commit()

    if not current_commit:
        print("No commits to branch from")
        return

    os.makedirs(os.path.dirname(branch_path), exist_ok=True)

    with open(branch_path, "w") as f:
        f.write(current_commit)

    print(f"Branch '{name}' created at {current_commit}")


def merge_branch(name):
    branch_path = os.path.join(".snapgit", "refs", "heads", name)

    if not os.path.exists(branch_path):
        print("Branch not found")
        return

    current_commit = get_current_commit()

    with open(branch_path, "r") as f:
        other_commit = f.read().strip()

    if current_commit == other_commit:
        print("Already up to date")
        return

    # Read other commit files (simple strategy: take their version)
    path = os.path.join(".snapgit", "objects", other_commit)

    with open(path, "rb") as f:
        data = f.read()
