# pyshell

A POSIX-ish shell implemented in Python, supporting builtins (`cd`, `pwd`,
`echo`, and more), external program execution, pipelines, and tab completion.

## Setup

```sh
make setup
```

Creates a virtual environment and installs dependencies with `uv`.

## Run

```sh
make run
```

To pass arguments to the shell:

```sh
make run ARGS="-c 'echo hi'"
```

## Project layout

The entry point is [app/main.py](app/main.py).
