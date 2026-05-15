import sys
from .commands.init_repo import init_repo
from .commands.add_file import add_file
from .commands.commit import create_commit
from .commands.checkout import checkout
from .commands.branch import create_branch
from .commands.merge import merge
from .commands.diff import diff
from .utils import read_object, show_status, log_commits


# Command help text
COMMANDS_HELP = {
    "init": {
        "usage": "snapgit init",
        "description": "Initialize a new SnapGit repository in the current directory.",
        "example": "snapgit init"
    },
    "add": {
        "usage": "snapgit add <filename>",
        "description": "Stage files for commit.",
        "example": "snapgit add file.txt"
    },
    "commit": {
        "usage": "snapgit commit <message>",
        "description": "Create a new commit with staged files.",
        "example": "snapgit commit 'Initial commit'"
    },
    "checkout": {
        "usage": "snapgit checkout <branch|commit>",
        "description": "Switch to a branch or checkout a commit (detached HEAD).",
        "example": "snapgit checkout main"
    },
    "branch": {
        "usage": "snapgit branch <name>",
        "description": "Create a new branch from the current commit.",
        "example": "snapgit branch feature"
    },
    "merge": {
        "usage": "snapgit merge <branch>",
        "description": "Merge another branch into the current branch.",
        "example": "snapgit merge feature"
    },
    "diff": {
        "usage": "snapgit diff [<commit1>] [<commit2>]",
        "description": "Show differences between commits.",
        "example": "snapgit diff main feature"
    },
    "log": {
        "usage": "snapgit log",
        "description": "Display repository history.",
        "example": "snapgit log"
    },
    "status": {
        "usage": "snapgit status",
        "description": "Show the working tree status.",
        "example": "snapgit status"
    },
    "cat-file": {
        "usage": "snapgit cat-file <hash>",
        "description": "Display object contents by hash.",
        "example": "snapgit cat-file abc123def456..."
    },
}

GLOBAL_HELP = """SnapGit - A Git-like Version Control System

Usage:
  snapgit <command> [options]
  snapgit --help
  snapgit --version

Commands:
  init        Initialize a repository
  add         Stage files
  commit      Create commit
  checkout    Switch branches/commits
  branch      Create branches
  merge       Merge branches
  diff        Show differences
  log         Display history
  status      Show repository status
  cat-file    Inspect stored objects

Run 'snapgit <command> --help' for detailed usage.
"""

def print_help(command=None):
    """Print help for a command or global help."""
    if command is None:
        print(GLOBAL_HELP)
        return
    
    if command in COMMANDS_HELP:
        info = COMMANDS_HELP[command]
        print(f"Usage: {info['usage']}")
        print(f"\n{info['description']}")
        print(f"\nExample: {info['example']}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(2)

def require_argument(argv, command_name, argument_name):
    """Validate required command arguments."""
    if len(argv) < 3:
        print(f"Error: missing {argument_name}", file=sys.stderr)
        print(
            f"Usage: {COMMANDS_HELP[command_name]['usage']}",
            file=sys.stderr
        )
        sys.exit(2)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print_help()
        sys.exit(2)

    command = argv[1]

    # Handle help flags
    if command in ("--help", "-h", "help"):
        if len(argv) > 2:
            print_help(argv[2])
        else:
            print_help()
        sys.exit(0)
    
    if command in ("--version", "-v", "version"):
        print("SnapGit version 0.5.0")
        sys.exit(0)

    try:
        if command == "init":
            init_repo()

        elif command == "add":
            require_argument(argv, "add", "filename")
            add_file(argv[2])

        elif command == "cat-file":
            if len(argv) < 3:
                print("Error: missing hash", file=sys.stderr)
                print(f"Usage: {COMMANDS_HELP['cat-file']['usage']}", file=sys.stderr)
                sys.exit(2)
            read_object(argv[2])

        elif command == "commit":
            require_argument(argv, "commit", "commit message")
            create_commit(argv[2])

        elif command == "checkout":
            if len(argv) < 3:
                print("Error: missing branch or commit", file=sys.stderr)
                print(f"Usage: {COMMANDS_HELP['checkout']['usage']}", file=sys.stderr)
                sys.exit(2)
            checkout(argv[2])

        elif command == "branch":
            if len(argv) < 3:
                print("Error: missing branch name", file=sys.stderr)
                print(f"Usage: {COMMANDS_HELP['branch']['usage']}", file=sys.stderr)
                sys.exit(2)
            create_branch(argv[2])

        elif command == "merge":
            if len(argv) < 3:
                print("Error: missing branch name", file=sys.stderr)
                print(f"Usage: {COMMANDS_HELP['merge']['usage']}", file=sys.stderr)
                sys.exit(2)
            merge(argv[2])

        elif command == "diff":
            if len(argv) == 2:
                diff()
            elif len(argv) == 3:
                diff(argv[2])
            elif len(argv) == 4:
                diff(argv[2], argv[3])
            else:
                print("Error: too many arguments", file=sys.stderr)
                print(f"Usage: {COMMANDS_HELP['diff']['usage']}", file=sys.stderr)
                sys.exit(2)

        elif command == "status":
            show_status()

        elif command == "log":
            log_commits()

        else:
            print(f"Error: unknown command '{command}'", file=sys.stderr)
            print(f"Use 'snapgit --help' for usage information.", file=sys.stderr)
            sys.exit(2)
            
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\nAborted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()