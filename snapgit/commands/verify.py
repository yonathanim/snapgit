import os

def verify_repository():
    required_paths = [
        ".snapgit",
        ".snapgit/objects",
        ".snapgit/refs",
        ".snapgit/HEAD",
    ]

    missing = []

    for path in required_paths:
        if not os.path.exists(path):
            missing.append(path)

    if missing:
        print("Repository verification failed:")
        for path in missing:
            print(f"  missing: {path}")
        return

    print("Repository verification successful")