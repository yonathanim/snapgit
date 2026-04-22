import sys
from .commands.init_repo import init_repo
from .commands.add_file import add_file
from .commands.commit import create_commit
from .commands.checkout import checkout
from .commands.branch import create_branch, merge_branch
from .utils import read_object, show_status, log_commits


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print("Please provide a command")
        return

    command = argv[1]

    if command == "init":
        init_repo()

    elif command == "add":
        if len(argv) < 3:
            print("Provide a filename")
        else:
            add_file(argv[2])

    elif command == "cat-file":
        if len(argv) < 3:
            print("Provide a hash")
        else:
            read_object(argv[2])

    elif command == "commit":
        if len(argv) < 3:
            print("Provide a commit message")
        else:
            create_commit(argv[2])
    elif command == "checkout":
        if len(argv) < 3:
            print("Provide a name")
        else:
            checkout(argv[2])
    elif command == "branch":
        if len(argv) < 3:
            print("Provide a branch name")
        else:
            create_branch(argv[2])
    elif command == "merge":
        if len(argv) < 3:
            print("Provide branch name")
        else:
            merge_branch(argv[2])
    elif command == "status":
        show_status()
    elif command == "log":
        log_commits()
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()
