import os


def _expand_variable(name):
    from .commands import DECLARED_VARIABLES

    if name in DECLARED_VARIABLES:
        return DECLARED_VARIABLES[name]
    return os.environ.get(name, "")


def tokenize(input_string):
    tokens = []
    current = ""
    i = 0
    in_single_quotes = False
    in_double_quotes = False

    while i < len(input_string):
        char = input_string[i]

        if char == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
            i += 1
            continue

        if char == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
            i += 1
            continue

        if not in_single_quotes and not in_double_quotes and char.isspace():
            if current:
                tokens.append(current)
                current = ""
            i += 1
            continue

        if char == "$" and not in_single_quotes:
            if i + 1 < len(input_string) and input_string[i + 1] == "{":
                close_idx = input_string.find("}", i + 2)
                if close_idx != -1:
                    current += _expand_variable(input_string[i + 2 : close_idx])
                    i = close_idx + 1
                    continue

            j = i + 1
            if j < len(input_string) and (
                input_string[j].isalpha() or input_string[j] == "_"
            ):
                k = j
                while k < len(input_string) and (
                    input_string[k].isalnum() or input_string[k] == "_"
                ):
                    k += 1
                current += _expand_variable(input_string[j:k])
                i = k
                continue

        if not in_single_quotes and not in_double_quotes:
            if char == '\\' and i + 1 < len(input_string):
                current += input_string[i + 1]
                i += 2
                continue
            
        if not in_single_quotes and in_double_quotes:
            if char == '\\' and i + 1 < len(input_string):
                second_char = input_string[i + 1]
                if second_char in ['"', '\\', '$', '`', '\n']:
                    current += input_string[i + 1]
                    i += 2
                    continue

        current += char
        i += 1

    if current:
        tokens.append(current)

    return tokens


def split_pipeline(tokens):
    segments = [[]]
    for token in tokens:
        if token == "|":
            segments.append([])
        else:
            segments[-1].append(token)
    return [segment for segment in segments if segment]
