# Repository Invariants

SnapGit relies on several repository invariants to maintain internal consistency.

## Object Immutability

Stored objects are never modified after creation.

## Deterministic Hashing

Identical content must always produce identical object hashes.

## Commit Parent Integrity

Each commit reference must point to valid parent commits.

## HEAD Consistency

HEAD must always reference a valid branch or commit state.

## Repository Safety

Repository operations should fail predictably when invalid states are detected.

## Index Consistency

The staging index must reflect the latest staged object references.