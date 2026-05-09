"""SnapGit Commit Graph.

High-level commit history traversal and analysis.

Implements:
- CommitGraph: Traverse commit history following parent pointers
- Get commits in order
- Format for display
- Future: merge-base, reachability, etc.
"""

from typing import List, Optional, Dict, Tuple
from .objects import ObjectStore
from .refs import RefManager


class CommitNode:
    """Represents a commit in the graph."""
    
    def __init__(self, hash_value: str, parents: List[str], 
                 author: str, date: str, message: str, tree_data: str):
        self.hash = hash_value
        self.parents = parents
        self.author = author
        self.date = date
        self.message = message
        self.tree_data = tree_data
    
    def __repr__(self) -> str:
        return f"CommitNode({self.hash[:8]}...)"


class CommitGraph:
    """
    Git-like commit graph for history traversal.
    
    Provides high-level operations on the commit DAG (directed acyclic graph).
    """
    
    @staticmethod
    def parse_commit(commit_hash: str) -> Optional[CommitNode]:
        """
        Parse a commit object into structured data.
        
        Returns None if commit not found or malformed.
        """
        try:
            obj_type, content = ObjectStore.read_object(commit_hash)
            if obj_type != "commit":
                return None
            
            content_str = content.decode("utf-8")
            lines = content_str.split("\n")
            
            parents = []
            author = ""
            date = ""
            message = ""
            tree_data = ""
            tree_start = 0
            
            # Parse header lines
            for i, line in enumerate(lines):
                if line.startswith("parent "):
                    parents.append(line[7:])  # "parent " = 7 chars
                elif line.startswith("author "):
                    author = line[7:]
                elif line.startswith("date "):
                    date = line[5:]
                elif line.startswith("message "):
                    message = line[8:]
                    tree_start = i + 1
                    break
            
            # Everything after message is tree data
            if tree_start > 0 and tree_start < len(lines):
                tree_data = "\n".join(lines[tree_start:])
            
            return CommitNode(
                hash_value=commit_hash,
                parents=parents,
                author=author,
                date=date,
                message=message,
                tree_data=tree_data
            )
        except Exception:
            return None
    
    @staticmethod
    def get_history(commit_hash: Optional[str], max_count: Optional[int] = None) -> List[CommitNode]:
        """
        Get commit history in reverse chronological order.
        
        Follows parent pointers from given commit to root.
        
        Args:
            commit_hash: Starting commit (None = current HEAD)
            max_count: Maximum commits to return (None = all)
        
        Returns:
            List of CommitNode objects
        """
        if commit_hash is None:
            commit_hash = RefManager.get_current_commit()
        
        if commit_hash is None:
            return []
        
        history = []
        visited = set()
        
        def traverse(h: str) -> None:
            if h in visited:
                return
            if max_count is not None and len(history) >= max_count:
                return
            
            visited.add(h)
            node = CommitGraph.parse_commit(h)
            if node is None:
                return
            
            history.append(node)
            
            # Traverse parents (depth-first)
            for parent_hash in node.parents:
                traverse(parent_hash)
        
        traverse(commit_hash)
        return history
    
    @staticmethod
    def format_log(commit_hash: Optional[str] = None) -> str:
        """
        Format commit history for display.
        
        Similar to: git log --oneline --decorate
        """
        history = CommitGraph.get_history(commit_hash)
        
        if not history:
            return "No commits yet."
        
        output = []
        for node in history:
            # Format: <hash> (<branch>) <author> <message>
            hash_short = node.hash[:12]
            
            # Try to find which branches point here
            branches = []
            for branch in RefManager.list_branches():
                if RefManager.get_branch_commit(branch) == node.hash:
                    branches.append(branch)
            
            branch_str = f" ({', '.join(branches)})" if branches else ""
            
            line = f"{hash_short}{branch_str} {node.author} {node.message}"
            output.append(line)
        
        return "\n".join(output)
    
    @staticmethod
    def get_merge_base(commit1: str, commit2: str) -> Optional[str]:
        """
        Find common ancestor of two commits (for future merge support).
        
        Returns hash of merge base, or None if none found.
        """
        # Get all ancestors of commit1
        ancestors1 = set()
        history1 = CommitGraph.get_history(commit1)
        for node in history1:
            ancestors1.add(node.hash)
        
        # Find first ancestor of commit2 that's in ancestors1
        history2 = CommitGraph.get_history(commit2)
        for node in history2:
            if node.hash in ancestors1:
                return node.hash
        
        return None
    
    @staticmethod
    def is_ancestor(ancestor: str, descendant: str) -> bool:
        """Check if ancestor is an ancestor of descendant."""
        history = CommitGraph.get_history(descendant)
        for node in history:
            if node.hash == ancestor:
                return True
        return False
