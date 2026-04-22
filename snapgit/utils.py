import os
import hashlib

def read_file(filepath):
    with open(filepath, "rb") as f:
        return f.read()


def get_hash(content):
    header = f"blob {len(content)}\0".encode()
    full_data = header + content
    return hashlib.sha1(full_data).hexdigest(), full_data


def store_object(hash_value, content):
    path = os.path.join(".snapgit", "objects", hash_value)

    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(content)


def update_index(filename, hash_value):
    index_path = os.path.join(".snapgit", "index")

    entries = {}

    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) != 2:
                    continue
                name, h = parts
                entries[name] = h

    entries[filename] = hash_value

    with open(index_path, "w") as f:
        for name in sorted(entries.keys()):
            f.write(f"{name} {entries[name]}\n")


def read_index():
    index_path = os.path.join(".snapgit", "index")

    if not os.path.exists(index_path):
        return []

    with open(index_path, "r") as f:
        return f.readlines()


def get_head_ref():
    with open(os.path.join(".snapgit", "HEAD"), "r") as f:
        ref = f.read().strip()
    return ref.split(" ")[1]


def get_current_commit():
    ref_path = os.path.join(".snapgit", get_head_ref())

    if os.path.exists(ref_path):
        with open(ref_path, "r") as f:
            return f.read().strip()

    return None


def read_object(hash_value):
    path = os.path.join(".snapgit", "objects", hash_value)

    if not os.path.exists(path):
        print("Object not found")
        return

    with open(path, "rb") as f:
        data = f.read()

    header, content = data.split(b"\0", 1)

    header = header.decode()
    parts = header.split(" ", 1)
    obj_type = parts[0]
    size_str = parts[1] if len(parts) > 1 else str(len(content))

    try:
        content_str = content.decode()
    except UnicodeDecodeError:
        content_str = content.decode(errors="replace")

    print(f"TYPE: {obj_type}")
    print(f"SIZE: {size_str}")
    print(f"CONTENT: {content_str}")


def log_commits():
    commit_hash = get_current_commit()

    if not commit_hash:
        print("No commits yet.")
        return

    while commit_hash:
        path = os.path.join(".snapgit", "objects", commit_hash)

        if not os.path.exists(path):
            print("Broken commit chain.")
            return

        with open(path, "rb") as f:
            data = f.read()

        header, content = data.split(b"\0", 1)
        content_str = content.decode(errors="replace")

        print(f"commit {commit_hash}")

        parent = None

        for line in content_str.split("\n"):
            if line.startswith("parent "):
                parent = line.split(" ", 1)[1]
            elif line.startswith("message "):
                print(f"message {line.split(' ', 1)[1]}")

        print()

        commit_hash = parent


def show_status():
    print("On branch", get_head_ref().split("/")[-1])
    print()

    index_entries = read_index()

    if not index_entries:
        print("No files staged")
        return

    print("Staged files:")
    for entry in index_entries:
        filename = entry.split(" ")[0]
        print(f"- {filename}")
