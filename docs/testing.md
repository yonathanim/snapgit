# Testing and Verification

SnapGit uses automated tests to verify repository behavior and internal consistency.

## Test Coverage

The test suite validates:

- object storage
- commit creation
- branch operations
- checkout behavior
- merge functionality
- diff generation
- repository safety validation

## Running Tests

```bash
pytest tests/ -v
```

## Repository Validation

Safety checks are used to detect invalid repository states and corrupted references.

## Testing Philosophy

The project emphasizes deterministic behavior and predictable repository state transitions.

Tests focus on:
- correctness
- repository integrity
- graph consistency
- command reliability
```