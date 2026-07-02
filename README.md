# pyshell

A POSIX-ish command-line shell implemented in Python. `pyshell` provides an
interactive read-eval loop with pipelines, I/O redirection, background jobs,
shell variables, persistent history, and tab completion, on top of a small,
pluggable builtin-command registry.

## Features

- **Builtin commands** — `cd`, `pwd`, `echo`, `type`, `exit`, `history`,
  `jobs`, `declare`, `complete` (see [Builtins](#builtins))
- **External command execution** — resolves executables from `PATH`
  (honors `PATHEXT` on Windows)
- **Pipelines** — chain builtins and external programs with `|`
- **I/O redirection** — `>`, `>>`, `1>`, `1>>`, `2>`, `2>>`
- **Background jobs** — trailing `&` backgrounds a command; `jobs` reports
  status, completed jobs are reaped between prompts
- **Shell variables** — `declare NAME=value`, expanded as `$NAME` / `${NAME}`,
  falling back to the process environment
- **Quoting & escaping** — single quotes, double quotes, and backslash
  escapes, matching common POSIX shell semantics
- **Tab completion** — completes builtins, executables on `PATH`, and
  filesystem paths; supports custom completion scripts registered via
  `complete -C`
- **Persistent history** — readline history is loaded/saved across sessions
  (`$HISTFILE`, defaulting to `~/.pyshell_history`), with `history -r/-w/-a`
  for manual control

## Requirements

- Python >= 3.12 (developed against 3.14; see [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) for dependency management and running the
  project
- On Windows, [`pyreadline3`](https://pypi.org/project/pyreadline3/) is
  installed automatically as a `readline` fallback

## Installation

```sh
git clone <repo-url>
cd pyshell
make setup
```

`make setup` runs `uv sync`, creating a `.venv` and installing runtime and
development dependencies.

## Usage

Start an interactive session:

```sh
make run
```

or, without `make`:

```sh
uv run pyshell
```

Example session:

```
$ declare NAME=world
$ echo "hello $NAME"
hello world
$ ls | grep py
pyshell
$ echo done > out.txt
$ sleep 5 &
[1] 12345
$ jobs
[1]+  Running                 sleep 5 &
```

## Builtins

| Command    | Description                                              |
|------------|-----------------------------------------------------------|
| `cd`       | Change directory (`cd` alone or `cd ~` goes to `$HOME`)   |
| `pwd`      | Print the current working directory                       |
| `echo`     | Print arguments, honoring output redirection               |
| `type`     | Report whether a command is a builtin or an external file  |
| `exit`     | Exit the shell, optionally with a status code               |
| `history`  | Show, load (`-r`), or persist (`-w`/`-a`) command history    |
| `jobs`     | List background jobs and their status                       |
| `declare`  | Define a shell variable, or print one with `-p`             |
| `complete` | Register (`-C`), inspect (`-p`), or remove (`-r`) tab-completion scripts for a command |

Custom builtins are added by dropping a module in
[pyshell/builtins/](pyshell/builtins/) and registering it with
`@registry.register("name")`; import it in
[pyshell/builtins/\_\_init\_\_.py](pyshell/builtins/__init__.py) so it gets
loaded at startup.

## Project layout

```
pyshell/
├── main.py                    # Entry point (`pyshell` console script)
├── shell.py                   # Read-eval loop, session wiring
├── context.py                 # Per-session state (ShellContext)
├── registry.py                # Builtin command registry
├── tokenizer.py                # Lexing, quoting/escaping, pipeline splitting
├── autocomplete.py            # readline tab-completion
├── history.py                  # readline history persistence
├── constants.py                # Redirection operators, enums
├── builtins/                  # One module per builtin command
│   ├── cd.py
│   ├── pwd.py
│   ├── echo.py
│   ├── type_cmd.py
│   ├── exit_cmd.py
│   ├── history_cmd.py
│   ├── jobs_cmd.py
│   ├── declare_cmd.py
│   └── complete_cmd.py
└── execution/
    ├── executor.py             # Command dispatch, external execution, pipelines
    ├── redirection.py          # Redirection parsing and output routing
    └── jobs.py                  # Background job table
```

## Development

```sh
make setup    # install dependencies
make run      # start the shell
make lint     # ruff check
make format   # ruff format
make clean    # clear the uv cache
```

[Ruff](https://docs.astral.sh/ruff/) is configured in
[pyproject.toml](pyproject.toml) for linting and formatting
(`E`, `F`, `I`, `UP`, `B`, `SIM` rule sets, 100-column lines, double quotes).

### Pre-commit hooks

This repo uses [pre-commit](https://pre-commit.com/) to run Ruff on every
commit:

```sh
uv run pre-commit install
```

## Contributing

Issues and pull requests are welcome. Please run `make lint` and
`make format` before submitting changes.
