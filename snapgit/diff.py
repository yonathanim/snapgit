"""
SnapGit Diff Engine.

Compares file snapshots and generates unified diffs.

Features:
- Parse tree data to extract file contents from blobs
- Line-by-line comparison between two versions
- Unified diff format output (Git-style)
- Support for additions, deletions, modifications
"""

from typing import Dict, List, Tuple, Optional
from .objects import ObjectStore


class DiffLine:
    """Represents a single diff line."""
    
    # Type constants
    CONTEXT = " "
    ADDED = "+"
    REMOVED = "-"
    
    def __init__(self, line_type: str, content: str, line_num_old: Optional[int] = None, 
                 line_num_new: Optional[int] = None):
        self.type = line_type  # " ", "+", "-"
        self.content = content
        self.line_num_old = line_num_old
        self.line_num_new = line_num_new
    
    def __repr__(self) -> str:
        return f"{self.type}{self.content}"


class DiffEngine:
    """Generate diffs between file snapshots."""
    
    @staticmethod
    def parse_tree_data(tree_data: str) -> Dict[str, str]:
        """
        Parse tree_data into filename -> blob_hash mapping.
        
        Format: "filename1 hash1\nfilename2 hash2\n..."
        
        Returns:
            Dict mapping filename to blob hash
        """
        tree = {}
        if not tree_data or not tree_data.strip():
            return tree
        
        for line in tree_data.strip().split("\n"):
            if not line.strip():
                continue
            
            parts = line.rsplit(" ", 1)  # rsplit to handle spaces in filenames
            if len(parts) == 2:
                filename, blob_hash = parts
                tree[filename] = blob_hash
        
        return tree
    
    @staticmethod
    def get_file_content(blob_hash: str) -> str:
        """
        Retrieve file content from blob hash.
        
        Args:
            blob_hash: SHA1 hash of blob object
            
        Returns:
            File content as string
            
        Raises:
            Exception if blob not found
        """
        try:
            obj_type, content_bytes = ObjectStore.read_object(blob_hash)
            if obj_type != "blob":
                raise ValueError(f"Expected blob, got {obj_type}")
            return content_bytes.decode("utf-8")
        except Exception as e:
            raise Exception(f"Failed to read blob {blob_hash}: {e}")
    
    @staticmethod
    def unified_diff(file1_content: str, file2_content: str, 
                     filename: str = "file") -> str:
        """
        Generate unified diff between two file versions.
        
        Args:
            file1_content: Original file content
            file2_content: Modified file content
            filename: Filename for diff header
            
        Returns:
            Unified diff as string
        """
        lines1 = file1_content.splitlines(keepends=False)
        lines2 = file2_content.splitlines(keepends=False)
        
        # Simple diff algorithm: compare line by line
        # For Phase 4, we use a basic approach; future: implement Myers' algorithm
        
        diff_lines: List[DiffLine] = []
        
        # Use a simple LCS-based approach
        diff_lines = DiffEngine._simple_line_diff(lines1, lines2)
        
        # Format output
        if not diff_lines:
            return ""  # No difference
        
        output = []
        output.append(f"--- a/{filename}")
        output.append(f"+++ b/{filename}")
        
        # Add hunk header
        old_count = sum(1 for l in diff_lines if l.type in (" ", "-"))
        new_count = sum(1 for l in diff_lines if l.type in (" ", "+"))
        output.append(f"@@ -1,{old_count} +1,{new_count} @@")
        
        # Add diff lines
        for diff_line in diff_lines:
            output.append(str(diff_line))
        
        return "\n".join(output)
    
    @staticmethod
    def _simple_line_diff(lines1: List[str], lines2: List[str]) -> List[DiffLine]:
        """
        Simple diff algorithm - for now, show all removals then additions.
        
        This is not optimal but correct. Future: implement Myers' LCS.
        """
        diff_lines: List[DiffLine] = []
        
        # Naive approach: match lines greedily from start
        i, j = 0, 0
        
        # Find common prefix
        while i < len(lines1) and j < len(lines2) and lines1[i] == lines2[j]:
            diff_lines.append(DiffLine(DiffLine.CONTEXT, lines1[i]))
            i += 1
            j += 1
        
        # Find common suffix
        i_end = len(lines1) - 1
        j_end = len(lines2) - 1
        
        while i_end >= i and j_end >= j and lines1[i_end] == lines2[j_end]:
            i_end -= 1
            j_end -= 1
        
        # Add changed section
        # First: removed lines from file1
        for k in range(i, i_end + 1):
            diff_lines.append(DiffLine(DiffLine.REMOVED, lines1[k]))
        
        # Then: added lines from file2
        for k in range(j, j_end + 1):
            diff_lines.append(DiffLine(DiffLine.ADDED, lines2[k]))
        
        # Finally: common suffix
        for k in range(i_end + 1, len(lines1)):
            diff_lines.append(DiffLine(DiffLine.CONTEXT, lines1[k]))
        
        return diff_lines
    
    @staticmethod
    def diff_trees(tree_data1: str, tree_data2: str) -> str:
        """
        Compare two complete tree snapshots.
        
        Args:
            tree_data1: Tree data from first commit
            tree_data2: Tree data from second commit
            
        Returns:
            Full diff output for all changed files
        """
        tree1 = DiffEngine.parse_tree_data(tree_data1)
        tree2 = DiffEngine.parse_tree_data(tree_data2)
        
        all_files = set(tree1.keys()) | set(tree2.keys())
        output_parts = []
        
        for filename in sorted(all_files):
            hash1 = tree1.get(filename)
            hash2 = tree2.get(filename)
            
            # Skip if unchanged
            if hash1 == hash2:
                continue
            
            # File deleted
            if hash1 and not hash2:
                content1 = DiffEngine.get_file_content(hash1)
                file_diff = DiffEngine.unified_diff(content1, "", filename)
                if file_diff:
                    output_parts.append(file_diff)
                continue
            
            # File added
            if not hash1 and hash2:
                content2 = DiffEngine.get_file_content(hash2)
                file_diff = DiffEngine.unified_diff("", content2, filename)
                if file_diff:
                    output_parts.append(file_diff)
                continue
            
            # File modified
            content1 = DiffEngine.get_file_content(hash1)
            content2 = DiffEngine.get_file_content(hash2)
            file_diff = DiffEngine.unified_diff(content1, content2, filename)
            if file_diff:
                output_parts.append(file_diff)
        
        return "\n".join(output_parts) if output_parts else "No changes."
