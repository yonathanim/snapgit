# SnapGit Architecture

## Overview

SnapGit is a Git-inspired version control system implemented in Python.  
The repository is organized around modular components responsible for object storage, commit traversal, repository validation, and command execution.

## Repository Structure

```text
snapgit/
├── cli.py
├── objects.py
├── graph.py
├── safety.py
├── commands/
├── tests/
└── docs/
```

## Object Storage Layer

The storage layer manages content-addressable objects using SHA-1 hashing.

## Commit Graph Layer

The graph layer handles commit traversal, history lookup, and parent relationships.

## Command Layer

CLI commands are separated into dedicated modules for repository operations.

## Validation Layer

Repository validation prevents invalid repository states and corruption scenarios.

## Testing Strategy

SnapGit uses automated tests for repository operations, merge behavior, graph traversal, and safety validation.