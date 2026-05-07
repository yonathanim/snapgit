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
    """
    Get HEAD reference path (for compatibility).
    
    DEPRECATED: Use RefManager.get_head_ref() or RefManager.resolve_head()
    Returns: Branch path like "refs/heads/main"
    """
    from .refs import RefManager
    head_content = RefManager.get_head_ref()
    
    # If symbolic ref, extract the path
    if head_content.startswith("ref: "):
        return head_content[5:]
    
    # Fallback for detached state
    return "HEAD"


def get_current_commit():
    """
    Get current commit hash.
    
    DEPRECATED: Use RefManager.get_current_commit()
    """
    from .refs import RefManager
    return RefManager.get_current_commit()


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
    """
    Display commit history using CommitGraph.
    
    Shows full commit graph with proper formatting.
    """
    from .graph import CommitGraph
    
    output = CommitGraph.format_log()
    print(output)


def show_status():
    """
    Show repository status.
    
    Displays:
    - Current branch (or detached state)
    - Staged files
    """
    from .refs import RefManager
    
    commit, branch = RefManager.resolve_head()
    
    if branch:
        print(f"On branch {branch}")
    else:
        print(f"HEAD detached at {commit[:12] if commit else 'none'}")
    
    print()
    
    index_entries = read_index()
    
    if not index_entries:
        print("No files staged")
        return
    
    print("Staged files:")
    for entry in index_entries:
        filename = entry.split(" ")[0]
        print(f"- {filename}")
