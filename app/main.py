import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


def match_at_pos(text: str, pattern: str, is_end_of_text: bool) -> tuple[bool, str]:
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

    if pattern[0] == "$":
        # End of string anchor
        if not is_end_of_text:
            return False, ""
        return True, ""

    # Literal character
    match = text == pattern[0]
    if match:
        return True, pattern[1:]
    return False, pattern


def match_pattern(text: str, pattern: str) -> bool:
    pos = 0
    match = False
    is_end_of_text = False
    while True:
        try:
            text_at_pos = text[pos]
        except IndexError:
            is_end_of_text = True
            text_at_pos = ""

        match, pattern = match_at_pos(text_at_pos, pattern, is_end_of_text)

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
