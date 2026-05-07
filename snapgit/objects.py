"""
SnapGit Object Storage System.

This module implements Git-like content-addressable object storage.
Every object has a type, size, and content, and is addressed by its SHA1 hash.

Object Format:
    <type> <size>\0<content>
    
    Example: blob 13\0Hello, World!
    SHA1 hashed over the entire string (header + content).

This design enables:
- Immutability (content → hash → can't overwrite)
- Deduplication (same content → same hash)
- Integrity (recompute hash to detect corruption)
"""

import os
import hashlib
import time
from typing import Tuple, Optional


class ObjectStore:
    """
    Git-like content-addressable object storage.
    
    Handles low-level object I/O: writing, reading, validating.
    All operations are type-agnostic (blobs, commits, trees, etc.).
    """
    
    REPO_DIR = ".snapgit"
    OBJECTS_DIR = os.path.join(REPO_DIR, "objects")
    
    @staticmethod
    def _object_path(hash_value: str) -> str:
        """Get filesystem path for an object hash."""
        return os.path.join(ObjectStore.OBJECTS_DIR, hash_value)
    
    @staticmethod
    def _make_header(obj_type: str, size: int) -> bytes:
        """Create object header: type size\0"""
        return f"{obj_type} {size}\0".encode()
    
    @staticmethod
    def _compute_hash(obj_type: str, content: bytes) -> str:
        """
        Compute SHA1 hash of object.
        
        Hash is computed over: header + content
        This is identical to Git's object hashing.
        """
        header = ObjectStore._make_header(obj_type, len(content))
        full_data = header + content
        return hashlib.sha1(full_data).hexdigest()
    
    @staticmethod
    def write_object(obj_type: str, content: bytes) -> str:
        """
        Write an object to storage.
        
        Args:
            obj_type: Object type ("blob", "commit", etc.)
            content: Raw content bytes (without header)
            
        Returns:
            SHA1 hash of the object
            
        Behavior:
            - Computes hash from header + content
            - Writes full object to .snapgit/objects/<hash>
            - Skips if already exists (immutable)
        """
        hash_value = ObjectStore._compute_hash(obj_type, content)
        path = ObjectStore._object_path(hash_value)
        
        # Only write if not already present (immutability)
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            header = ObjectStore._make_header(obj_type, len(content))
            full_data = header + content
            with open(path, "wb") as f:
                f.write(full_data)
        
        return hash_value
    
    @staticmethod
    def read_object(hash_value: str) -> Tuple[str, bytes]:
        """
        Read an object from storage.
        
        Args:
            hash_value: SHA1 hash of object
            
        Returns:
            (obj_type, content) tuple
            
        Raises:
            FileNotFoundError: If object doesn't exist
            ValueError: If object header is malformed
        """
        path = ObjectStore._object_path(hash_value)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Object {hash_value} not found")
        
        with open(path, "rb") as f:
            raw_data = f.read()
        
        return ObjectStore.parse_object(raw_data)
    
    @staticmethod
    def object_exists(hash_value: str) -> bool:
        """Check if object exists in storage."""
        return os.path.exists(ObjectStore._object_path(hash_value))
    
    @staticmethod
    def parse_object(raw_data: bytes) -> Tuple[str, bytes]:
        """
        Parse a raw object (header + content).
        
        Args:
            raw_data: Raw bytes from object file
            
        Returns:
            (obj_type, content) tuple
            
        Raises:
            ValueError: If header is malformed
        """
        # Split at first \0
        try:
            header_bytes, content = raw_data.split(b"\0", 1)
        except ValueError:
            raise ValueError("Malformed object: no null separator found")
        
        # Decode header
        try:
            header = header_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Malformed object: header not UTF-8")
        
        # Parse "type size"
        parts = header.split(" ", 1)
        if len(parts) != 2:
            raise ValueError(f"Malformed object header: {header}")
        
        obj_type, size_str = parts
        
        # Validate size matches content
        try:
            size = int(size_str)
            if len(content) != size:
                raise ValueError(
                    f"Size mismatch: header says {size}, got {len(content)}"
                )
        except ValueError as e:
            raise ValueError(f"Invalid object size: {size_str}") from e
        
        return obj_type, content


# ============================================================================
# High-Level Object Creators (for commands)
# ============================================================================

def create_blob(file_content: bytes) -> str:
    """
    Create a blob object from file content.
    
    Args:
        file_content: Raw bytes from file
        
    Returns:
        SHA1 hash of the blob
    """
    return ObjectStore.write_object("blob", file_content)


def create_commit(message: str, parent: Optional[str] = None, tree_data: str = "",
                 author: str = "SnapGit User", date: Optional[str] = None,
                 parents: Optional[list] = None) -> str:
    """
    Create a commit object with metadata.
    
    Commit format (similar to Git):
        parent <hash>
        [parent <hash2>]  # For merge commits
        author <name>
        date <timestamp>
        message <msg>
        <tree-data>
    
    Args:
        message: Commit message
        parent: Single parent commit hash (backward compatible, None for first commit)
        parents: List of parent commit hashes (for merge commits, takes precedence over parent)
        tree_data: Tree/index data (file entries)
        author: Author name (default: "SnapGit User")
        date: Unix timestamp as string (default: current time)
        
    Returns:
        SHA1 hash of the commit
    """
    if date is None:
        date = str(int(time.time()))
    
    content_parts = []
    
    # Handle parents (prefer list over single)
    parent_list = parents if parents is not None else (
        [parent] if parent else []
    )
    
    for p in parent_list:
        content_parts.append(f"parent {p}")
    
    content_parts.append(f"author {author}")
    content_parts.append(f"date {date}")
    content_parts.append(f"message {message}")
    content_parts.append(tree_data)
    
    content = "\n".join(content_parts) + "\n"
    content_bytes = content.encode("utf-8")
    
    return ObjectStore.write_object("commit", content_bytes)


# ============================================================================
# Object Reading for Display (for cat-file, log, etc.)
# ============================================================================

def read_object_safe(hash_value: str) -> Optional[Tuple[str, bytes]]:
    """
    Safely read an object, handling errors gracefully.
    
    Returns None if object not found or malformed.
    """
    try:
        return ObjectStore.read_object(hash_value)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading object {hash_value}: {e}")
        return None
