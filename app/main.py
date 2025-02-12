import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


def match_at_pos(text: str, pattern: str) -> tuple[bool, str]:
    if pattern.startswith("[") and pattern.endswith("]"):
        end_of_group = pattern.index("]")
        rest_of_pattern = pattern[end_of_group + 1 :]

        chars = pattern.strip("[]")
        if chars.startswith("^"):
            # Negative characters group
            chars = chars.strip("^")
            return all(c != text for c in chars), rest_of_pattern
        else:
            # Positive character group
            return any(c == text for c in chars), rest_of_pattern
    if pattern.startswith("\\d"):
        digits = string.digits
        match = any(d == text for d in digits)
        if match:
            return True, pattern.replace("\\d", "", 1)
        return False, pattern
    if pattern.startswith("\\w"):
        alphanumerics = string.digits + string.ascii_letters
        match = any(a == text for a in alphanumerics)
        if match:
            return True, pattern.replace("\\w", "", 1)
        return False, pattern

    # Literal character
    match = text == pattern[0]
    if match:
        return True, pattern[1:]
    return False, pattern[1:]


def match_pattern(text: str, pattern: str) -> bool:
    pos = 0
    match = False
    while pos < len(text):
        match, pattern = match_at_pos(text[pos], pattern)
        if pattern:
            # If there's still a pattern to consume
            # it means we don't have a match yet
            match = False
        else:
            break
        pos += 1

    return match


def main():
    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    pattern = sys.argv[2]
    text = sys.stdin.read()

    match = match_pattern(text, pattern)

    if not match:
        print("not found!")
        exit(1)
    else:
        print("found!")
        exit(0)


if __name__ == "__main__":
    main()
