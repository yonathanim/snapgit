import os

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
