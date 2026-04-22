import os
from ..utils import read_file, get_hash, store_object, update_index


def add_file(filename):
    if not os.path.exists(".snapgit"):
        print("Not a SnapGit repository.")
        return

    if not os.path.exists(filename):
        print("File does not exist.")
        return

    content = read_file(filename)
    hash_value, full_data = get_hash(content)

    store_object(hash_value, full_data)
    update_index(filename, hash_value)

    print(f"Added {filename}")
