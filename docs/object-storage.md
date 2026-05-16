# Object Storage Architecture

SnapGit uses a content-addressable object storage model inspired by Git.

## Blob Objects

Files are stored as blob objects.

Each object contains:
- object type
- content size
- raw file contents

## Object Identity

Object identities are generated using SHA-1 hashing.

Example structure:

```text
blob <size>\0<content>
```

The SHA-1 hash of this binary representation becomes the object identifier.

## Immutability

Objects are immutable after creation.

Changing file contents creates a new object instead of modifying existing data.

## Storage Layout

Objects are stored inside:

```text
.snapgit/objects/
```

Each filename corresponds to its object hash.

## Advantages

This model provides:
- deterministic storage
- integrity verification
- deduplication behavior
- stable object references