# SnapGit

SnapGit is a minimal version control system built from scratch in Python. The goal of this project is to deeply understand how Git works internally by recreating its core mechanisms step by step.

## Overview

This project focuses on implementing the fundamental ideas behind Git:

- content-addressable storage
- staging area (index)
- commit history and references
- lightweight version tracking

Instead of treating Git as a black box, SnapGit rebuilds its core logic in a simplified and transparent way to strengthen low-level understanding of version control systems.

## Current Features

- Repository initialization (`init`)
- File staging (`add`)
- Basic object storage system (WIP)
- SHA-1 based hashing for content tracking

## Architecture

SnapGit stores data inside a hidden `.snapgit` directory:
.snapgit/ ├── objects/ ├── refs/ ├── HEAD

- `objects/` stores all data (file contents and commits)
- `refs/` stores branch pointers
- `HEAD` tracks the current branch

## Tech Stack

- Python
- File system operations
- SHA-1 hashing
- Low-level data modeling

## Roadmap

- Commit functionality (`commit`)
- Log history (`log`)
- Branching system
- Checkout system
- Diff between versions

## Why this project?

This project is built for learning how Git works internally by rebuilding its core features from scratch instead of using Git as a black box.
