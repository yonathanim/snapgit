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

    with open(index_path, "a") as f:
        f.write(f"{filename} {hash_value}\n")

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

# --------------------
# CLI
# --------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a command")
    else:
        command = sys.argv[1]

        if command == "init":
            init_repo()

        elif command == "add":
            if len(sys.argv) < 3:
                print("Provide a file name")
            else:
                add_file(sys.argv[2])

        else:
            print("Unknown command")