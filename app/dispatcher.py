from .commands import (
    change_directory,
    echo_command,
    exit_command,
    handle_complete_command,
    handle_declare_command,
    handle_external_command,
    handle_history_command,
    handle_jobs_command,
    present_working_directory,
    type_command,
)


def command_dispatcher(command, arguments):
    if command == "exit":
        exit_command()

    elif command == "pwd":
        present_working_directory(arguments)

    elif command == "cd":
        change_directory(arguments)

    elif command == "type":
        type_command(arguments)

    elif command == "echo":
        echo_command(arguments)

    elif command == "complete":
        handle_complete_command(arguments)

    elif command == "jobs":
        handle_jobs_command()

    elif command == "history":
        handle_history_command(arguments)

    elif command == "declare":
        handle_declare_command(arguments)

    else:
        handle_external_command(command, arguments)
