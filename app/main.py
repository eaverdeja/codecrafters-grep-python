import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


def match_at_pos(text: str, pattern: str, is_quantified: bool) -> tuple[bool, str]:
    if pattern.startswith("^"):
        # Start of string anchor
        pattern = pattern.lstrip("^")
        # Literal match
        match = text == pattern[0]
        if match:
            return True, pattern[1:]
        # If there's no match at the start, then short-circuit
        # the operation by returning an empty pattern
        return False, ""

    if pattern.startswith("[") and pattern.endswith("]"):
        # Character groups
        rest_of_pattern = pattern[pattern.index("]") + 1 :]

        chars = pattern.strip("[]")
        if chars.startswith("^"):
            # Negative characters group
            chars = chars.strip("^")
            return all(c != text for c in chars), rest_of_pattern
        else:
            # Positive character group
            return any(c == text for c in chars), rest_of_pattern

    if pattern.startswith(r"\d"):
        # Digits character class
        digits = string.digits
        match = any(d == text for d in digits)
        if match:
            return True, pattern.replace(r"\d", "", 1)
        return False, pattern

    if pattern.startswith(r"\w"):
        # Words character class
        alphanumerics = string.digits + string.ascii_letters
        match = any(a == text for a in alphanumerics)
        if match:
            return True, pattern.replace(r"\w", "", 1)
        return False, pattern

    if is_quantified:
        # One or more quantifier (+)
        quantified = pattern[0]
        match = text == quantified
        if match:
            return True, pattern[2:]
        return False, pattern[1:]

    # Literal character
    match = text == pattern[0]
    if match:
        return True, pattern[1:]
    return False, pattern


def match_pattern(text: str, pattern: str) -> bool:
    pos = 0
    match = False

    if pattern.endswith("$"):
        # End of string anchor
        # Reverse operation of start of string anchor
        pattern = pattern.replace("$", "^")[::-1]
        text = text[::-1]

    while True:
        try:
            text_at_pos = text[pos]
        except IndexError:
            text_at_pos = ""

        try:
            text_at_pattern = pattern.index(text_at_pos)
            is_quantified = pattern[text_at_pattern + 1] == "+"
        except (ValueError, IndexError):
            is_quantified = False

        match, pattern = match_at_pos(text_at_pos, pattern, is_quantified)

        if pattern:
            # If there's still a pattern to consume
            # it means we don't have a match yet
            match = False
        else:
            # Else there's nothing more to check
            break

        if pos > len(text):
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
