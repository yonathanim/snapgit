import os
import sys
import hashlib

# --------------------
# INIT
# --------------------
def init_repo():
    repo_name = ".snapgit"

    if os.path.exists(repo_name):
        print("Repository already initialized.")
        return

    os.mkdir(repo_name)
    os.mkdir(os.path.join(repo_name, "objects"))
    os.mkdir(os.path.join(repo_name, "refs"))

    with open(os.path.join(repo_name, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main\n")

    print("Initialized empty SnapGit repository.")

   
# --------------------
# ADD
# --------------------         
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




def read_object(hash_value):
    path = os.path.join(".snapgit", "objects", hash_value)

    if not os.path.exists(path):
        print("Object not found")
        return

    with open(path, "rb") as f:
        data = f.read()

    # Split header and content
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

    # Step 1: Read existing entries
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

    # Step 2: Update (overwrite)
    entries[filename] = hash_value

    # Step 3: Rewrite index file
    with open(index_path, "w") as f:
        for name in sorted(entries.keys()):
            f.write(f"{name} {entries[name]}\n")



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


def read_index():
    index_path = os.path.join(".snapgit", "index")

    if not os.path.exists(index_path):
        return []

    with open(index_path, "r") as f:
        return f.readlines()


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

# --------------------
# CLI
# --------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please provide a command")
    else:
        command = sys.argv[1]

        if command == "init":
            init_repo()

        elif command == "add":
            if len(sys.argv) < 3:
                print("Provide a filename")
            else:
                add_file(sys.argv[2])

        elif command == "cat-file":
            if len(sys.argv) < 3:
                print("Provide a hash")
            else:
                read_object(sys.argv[2])

        elif command == "commit":
            if len(sys.argv) < 3:
                print("Provide a commit message")
            else:
                create_commit(sys.argv[2])
        elif command == "checkout":
            if len(sys.argv) < 3:
                print("Provide a name")
            else:
                checkout(sys.argv[2])
        elif command == "branch":
            if len(sys.argv) < 3:
                print("Provide a branch name")
            else:
                create_branch(sys.argv[2])
        elif command == "merge":
            if len(sys.argv) < 3:
                print("Provide branch name")
            else:
                merge_branch(sys.argv[2])  
        elif command == "status":
            show_status()      
        elif command == "log":        
            log_commits()                           
        else:
            print("Unknown command")
