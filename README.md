# SnapGit

SnapGit is a minimal version control system built from scratch in Python. The goal of this project is to understand how Git works internally by recreating its core mechanisms step by step.

## Overview

This project focuses on implementing the fundamental ideas behind Git:
- content-addressable storage
- staging area (index)
- commit history and references

Instead of relying on Git as a black box, SnapGit rebuilds its core logic in a simplified and transparent way.

## Current Features

- Repository initialization (`init`)
- File staging (`add`)

## Architecture

SnapGit stores data inside a hidden `.snapgit` directory:


.snapgit/
├── objects/
├── refs/
├── HEAD

- `objects/` stores all data (file contents and commits)
- `refs/` stores branch pointers
- `HEAD` tracks the current branch

## Tech Stack

- Python
- File system operations
- SHA-1 hashing
