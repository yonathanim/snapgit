# SnapGit Command Reference

## Initialize Repository

```bash
snapgit init
```

Creates a new SnapGit repository.

---

## Add File

```bash
snapgit add file.txt
```

Stores file contents as a blob object and stages it.

---

## Create Commit

```bash
snapgit commit "message"
```

Creates a commit from staged files.

---

## View History

```bash
snapgit log
```

Displays commit history.

---

## Checkout Commit

```bash
snapgit checkout <commit_hash>
```

Restores repository state from a commit.

---

## Merge Branch

```bash
snapgit merge <branch>
```

Combines changes from another branch.