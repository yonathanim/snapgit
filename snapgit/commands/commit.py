import os
import hashlib
from ..utils import read_index, get_current_commit, store_object, get_head_ref


def create_commit(message):
    repo = ".snapgit"

    index_entries = read_index()

    if not index_entries:
        print("Nothing to commit.")
        return

    parent = get_current_commit()

    content = ""

    if parent:
        content += f"parent {parent}\n"

    content += f"message {message}\n"

    for entry in index_entries:
        content += entry

    content_bytes = content.encode()

    header = f"commit {len(content_bytes)}\0".encode()
    full_data = header + content_bytes

    commit_hash = hashlib.sha1(full_data).hexdigest()

    store_object(commit_hash, full_data)

    ref_path = os.path.join(repo, get_head_ref())
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)

    with open(ref_path, "w") as f:
        f.write(commit_hash)

    # clear index after commit
    open(os.path.join(repo, "index"), "w").close()

    print(f"Committed: {commit_hash}")
