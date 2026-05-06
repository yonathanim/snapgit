"""
SnapGit utilities for repository operations.

High-level repo operations: index management, refs, HEAD tracking.
Low-level object storage is now in objects.py.
"""

import os
from typing import Dict, List, Optional


def read_file(filepath: str) -> bytes:
    """Read file contents as bytes."""
    with open(filepath, "rb") as f:
        return f.read()


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


def read_object(hash_value: str) -> None:
    """
    Display an object's type, size, and content.
    Uses the ObjectStore for proper object reading.
    """
    from .objects import ObjectStore
    
    try:
        obj_type, content = ObjectStore.read_object(hash_value)
        
        print(f"TYPE: {obj_type}")
        print(f"SIZE: {len(content)}")
        
        # Try to decode as text; fallback to repr
        try:
            content_str = content.decode("utf-8")
        except UnicodeDecodeError:
            content_str = content.decode("utf-8", errors="replace")
        
        print(f"CONTENT: {content_str}")
        
    except FileNotFoundError:
        print("Object not found")
    except ValueError as e:
        print(f"Error reading object: {e}")


def log_commits() -> None:
    """Display commit history using the ObjectStore."""
    from .objects import ObjectStore
    
    commit_hash = get_current_commit()

    if not commit_hash:
        print("No commits yet.")
        return

    while commit_hash:
        try:
            obj_type, content = ObjectStore.read_object(commit_hash)
        except FileNotFoundError:
            print("Broken commit chain.")
            return
        except ValueError as e:
            print(f"Error reading commit: {e}")
            return
        
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
