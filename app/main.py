import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


def match_pattern(input_line: str, pattern: str):
    if pattern.startswith("[") and pattern.endswith("]"):
        chars = pattern.strip("[]")
        return any(c in input_line for c in chars)
    if pattern == "\\d":
        digits = string.digits
        return any(d in input_line for d in digits)
    if pattern == "\\w":
        alphanumerics = string.digits + string.ascii_letters
        return any(a in input_line for a in alphanumerics)
    if len(pattern) == 1:
        return pattern in input_line
    else:
        raise RuntimeError(f"Unhandled pattern: {pattern}")


def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
