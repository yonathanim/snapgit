"""
SnapGit Merge Engine.

Three-way merge with automatic conflict detection.

Features:
- Find merge base (common ancestor)
- Three-way merge algorithm
- Conflict detection and marker creation
- Merge commit generation
"""

from typing import Dict, Tuple, List, Optional
from .objects import ObjectStore
from .graph import CommitGraph
from .diff import DiffEngine


class ConflictMarker:
    """Represents a merge conflict."""
    
    def __init__(self, filename: str, ours_content: str, theirs_content: str):
        self.filename = filename
        self.ours_content = ours_content
        self.theirs_content = theirs_content
    
    def format_marker(self, ours_label: str = "HEAD", theirs_label: str = "MERGE") -> str:
        """Format conflict marker in Git style."""
        lines = [
            f"<<<<<<< {ours_label}",
            self.ours_content,
            "=======",
            self.theirs_content,
            f">>>>>>> {theirs_label}",
        ]
        return "\n".join(lines)


class MergeResult:
    """Result of a merge operation."""
    
    def __init__(self, success: bool, merged_tree: str, conflicts: List[ConflictMarker]):
        self.success = success  # True if no conflicts
        self.merged_tree = merged_tree
        self.conflicts = conflicts


class MergeEngine:
    """Three-way merge with conflict detection."""
    
    @staticmethod
    def merge(base_tree: str, ours_tree: str, theirs_tree: str,
              ours_label: str = "HEAD", theirs_label: str = "MERGE") -> MergeResult:
        """
        Perform three-way merge on tree snapshots.
        
        Args:
            base_tree: Common ancestor tree data
            ours_tree: Our (current branch) tree data
            theirs_tree: Their (branch to merge) tree data
            ours_label: Label for "ours" in conflicts (e.g., "HEAD")
            theirs_label: Label for "theirs" in conflicts (e.g., "feature")
            
        Returns:
            MergeResult with merged tree and conflict list
        """
        # Parse all three trees
        base_files = DiffEngine.parse_tree_data(base_tree)
        ours_files = DiffEngine.parse_tree_data(ours_tree)
        theirs_files = DiffEngine.parse_tree_data(theirs_tree)
        
        # Get all filenames
        all_files = set(base_files.keys()) | set(ours_files.keys()) | set(theirs_files.keys())
        
        merged_files: Dict[str, str] = {}  # filename -> blob_hash
        conflicts: List[ConflictMarker] = []
        
        for filename in all_files:
            base_hash = base_files.get(filename)
            ours_hash = ours_files.get(filename)
            theirs_hash = theirs_files.get(filename)
            
            # Try to merge this file
            merged_hash, conflict = MergeEngine._merge_file(
                filename, base_hash, ours_hash, theirs_hash,
                ours_label, theirs_label
            )
            
            if conflict is None:  # Successful merge
                if merged_hash is not None:
                    merged_files[filename] = merged_hash
            else:  # Conflict occurred
                conflicts.append(conflict)
                # Still include the file with conflict markers
                conflict_content = conflict.format_marker(ours_label, theirs_label)
                conflict_blob_hash = ObjectStore.write_object("blob", conflict_content.encode("utf-8"))
                merged_files[filename] = conflict_blob_hash
        
        # Build merged tree data
        merged_tree = MergeEngine._build_tree_data(merged_files)
        
        return MergeResult(
            success=len(conflicts) == 0,
            merged_tree=merged_tree,
            conflicts=conflicts
        )
    
    @staticmethod
    def _merge_file(filename: str, base_hash: Optional[str], ours_hash: Optional[str],
                    theirs_hash: Optional[str], ours_label: str, 
                    theirs_label: str) -> Tuple[Optional[str], Optional[ConflictMarker]]:
        """
        Merge a single file using three-way merge.
        
        Returns:
            (blob_hash, conflict_marker) tuple
            - If successful: (blob_hash, None)
            - If conflict: (None, ConflictMarker)
            - If deleted: (None, None)
        """
        # Case 1: No change
        if ours_hash == base_hash == theirs_hash:
            return ours_hash, None
        
        # Case 2: File deleted on one or both sides
        # Deletion conflict: one side deleted, other side modified
        if (ours_hash is None and theirs_hash is not None and base_hash is not None) or \
           (theirs_hash is None and ours_hash is not None and base_hash is not None):
            # One side deleted, other modified = conflict
            base_content = DiffEngine.get_file_content(base_hash) if base_hash else ""
            ours_content = DiffEngine.get_file_content(ours_hash) if ours_hash else ""
            theirs_content = DiffEngine.get_file_content(theirs_hash) if theirs_hash else ""
            
            if ours_hash is None and theirs_hash is not None:
                # We deleted it, they modified it
                conflict = ConflictMarker(filename, "", theirs_content)
            else:
                # They deleted it, we modified it
                conflict = ConflictMarker(filename, ours_content, "")
            
            return None, conflict
        
        # Case 3: Only one side changed
        if ours_hash == base_hash and theirs_hash != base_hash:
            # Only theirs changed
            return theirs_hash, None
        
        if theirs_hash == base_hash and ours_hash != base_hash:
            # Only ours changed
            return ours_hash, None
        
        # Case 4: Both sides changed
        # Check if they changed identically
        if ours_hash == theirs_hash:
            return ours_hash, None
        
        # Case 5: Both sides changed differently - CONFLICT
        base_content = DiffEngine.get_file_content(base_hash) if base_hash else ""
        ours_content = DiffEngine.get_file_content(ours_hash) if ours_hash else ""
        theirs_content = DiffEngine.get_file_content(theirs_hash) if theirs_hash else ""
        
        # Try simple auto-merge (no overlapping changes)
        merged_content, has_conflict = MergeEngine._three_way_line_merge(
            base_content, ours_content, theirs_content
        )
        
        if not has_conflict:
            # Auto-merge succeeded
            merged_hash = ObjectStore.write_object("blob", merged_content.encode("utf-8"))
            return merged_hash, None
        else:
            # Return conflict
            conflict = ConflictMarker(filename, ours_content, theirs_content)
            return None, conflict
    
    @staticmethod
    def _three_way_line_merge(base: str, ours: str, theirs: str) -> Tuple[str, bool]:
        """
        Three-way line-based merge.
        
        Simple approach: if same line changed in both, conflict.
        If only one side changed, auto-merge.
        
        Returns:
            (merged_content, has_conflict)
        """
        base_lines = base.splitlines(keepends=False)
        ours_lines = ours.splitlines(keepends=False)
        theirs_lines = theirs.splitlines(keepends=False)
        
        # For Phase 4: simple approach - accept if one side is unchanged
        # Future: implement more sophisticated 3-way line merge
        
        # If unchanged from base on one side, use the other
        if base_lines == ours_lines:
            return theirs, False
        if base_lines == theirs_lines:
            return ours, False
        
        # If both changed identically, no conflict
        if ours == theirs:
            return ours, False
        
        # For now: any other case is a conflict
        # Future: implement proper line-by-line 3-way merge with conflict detection
        return "", True  # Conflict marker will be created by caller
    
    @staticmethod
    def _build_tree_data(files: Dict[str, str]) -> str:
        """Build tree data from filename -> blob_hash mapping."""
        lines = []
        for filename in sorted(files.keys()):
            lines.append(f"{filename} {files[filename]}")
        return "\n".join(lines) + "\n" if lines else ""


class MergeOrchestrator:
    """High-level merge coordination."""
    
    @staticmethod
    def merge_branches(current_commit: str, target_commit: str,
                       current_branch: str, target_branch: str) -> Tuple[bool, str, List[str]]:
        """
        Merge target_branch into current_branch.
        
        Args:
            current_commit: Current branch tip commit
            target_commit: Target branch tip commit
            current_branch: Name of current branch
            target_branch: Name of target branch
            
        Returns:
            (success, merged_tree, conflict_files)
        """
        # Find merge base
        merge_base = CommitGraph.get_merge_base(current_commit, target_commit)
        
        if merge_base is None:
            return False, "", ["No common ancestor found"]
        
        # Get trees
        base_node = CommitGraph.parse_commit(merge_base)
        ours_node = CommitGraph.parse_commit(current_commit)
        theirs_node = CommitGraph.parse_commit(target_commit)
        
        if not all([base_node, ours_node, theirs_node]):
            return False, "", ["Failed to parse commits"]
        
        # Perform merge
        result = MergeEngine.merge(
            base_node.tree_data,
            ours_node.tree_data,
            theirs_node.tree_data,
            ours_label=current_branch,
            theirs_label=target_branch
        )
        
        conflict_files = [c.filename for c in result.conflicts]
        
        return result.success, result.merged_tree, conflict_files
