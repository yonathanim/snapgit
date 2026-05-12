# SnapGit Design Principles

## Content Addressable Storage
Objects are stored using SHA-1 hashes of their content.

## Immutable History
Commits are never modified once created.

## Deterministic State
Same input always produces same repository state.

## Separation of Concerns
Storage, graph, CLI, and safety layers are independent.

## Minimal Core Design
Focus on essential Git concepts only.