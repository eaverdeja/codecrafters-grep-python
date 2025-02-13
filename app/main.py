import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


def match_at_pos(
    text: str, pattern: str, quantifier: str | None, occurrences: int
) -> tuple[bool, str, int]:
    print(text, pattern, quantifier, occurrences)
    if pattern.startswith("^"):
        # Start of string anchor
        pattern = pattern.lstrip("^")
        # Literal match
        match = text == pattern[0]
        if match:
            return True, pattern[1:], occurrences
        # If there's no match at the start, then short-circuit
        # the operation by returning an empty pattern
        return False, "", occurrences

    if pattern.startswith("[") and pattern.endswith("]"):
        # Character groups
        rest_of_pattern = pattern[pattern.index("]") + 1 :]

        chars = pattern.strip("[]")
        if chars.startswith("^"):
            # Negative characters group
            chars = chars.strip("^")
            return all(c != text for c in chars), rest_of_pattern, occurrences
        else:
            # Positive character group
            return any(c == text for c in chars), rest_of_pattern, occurrences

    if pattern.startswith(r"\d"):
        # Digits character class
        digits = string.digits
        match = any(d == text for d in digits)
        if match:
            return True, pattern.replace(r"\d", "", 1), occurrences
        return False, pattern, occurrences

    if pattern.startswith(r"\w"):
        # Words character class
        alphanumerics = string.digits + string.ascii_letters
        match = any(a == text for a in alphanumerics)
        if match:
            return True, pattern.replace(r"\w", "", 1), occurrences
        return False, pattern, occurrences

    if quantifier:
        quantified = pattern[0]
        if quantifier == "+":
            # One or more quantifier (+)
            match = text == quantified
        elif quantifier == "?":
            match = True if occurrences == 0 else text == quantified
        if match:
            occurrences += 1
            return True, pattern[2:], occurrences
        return False, pattern[1:], occurrences

    # Literal character
    match = text == pattern[0]
    if match:
        return True, pattern[1:], occurrences
    return False, pattern, occurrences


def match_pattern(text: str, pattern: str) -> bool:
    pos = 0
    occurrences = 0
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

        quantifier = None
        if pattern[1] in ("?", "+"):
            try:
                text_at_pattern = pattern.index(text_at_pos)
                quantifier = (
                    pattern[text_at_pattern + 1]
                    if pattern[text_at_pattern + 1] in ("?", "+")
                    else None
                )
            except (ValueError, IndexError):
                pass

        match, pattern, occurrences = match_at_pos(
            text_at_pos, pattern, quantifier, occurrences
        )

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
