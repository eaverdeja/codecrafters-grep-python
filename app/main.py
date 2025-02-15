import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


def match_at_pos(
    text: str, pattern: str, quantifier: str | None, occurrences: int
) -> tuple[bool, str, int]:
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

    if quantifier and text:
        quantified = pattern[0]

        if quantifier == "+":
            # One or more quantifier (+)
            if not text == quantified:
                if occurrences > 0:
                    return text == pattern[2], pattern[3:], -1
                return False, pattern, -1
            occurrences = max(1, occurrences + 1)
            return True, pattern, occurrences
        elif quantifier == "?":
            # Zero or more quantifier (?)
            if text == quantified:
                return True, pattern[2:], 1
            return text == pattern[2], pattern[3:], 0

    # Literal character
    match = text == pattern[0] if pattern else False

    return (True, pattern[1:], occurrences) if match else (False, pattern, occurrences)


def match_pattern(text: str, pattern: str) -> bool:
    pos = 0
    occurrences = -1

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

        quantifier = (
            pattern[1] if len(pattern) > 1 and pattern[1] in ("+", "?") else None
        )

        match, new_pattern, new_occurrences = match_at_pos(
            text_at_pos, pattern, quantifier, occurrences
        )

        # If we're counting the optional quantifier,
        # we can't consume our input string or else
        # we won't be able to check for the empty case
        if quantifier == "?" and new_pattern == pattern:
            continue
        # For the '+' quantifier, only advance the pattern
        # if we're done matching the repeated char
        if quantifier and new_pattern == pattern:
            pattern = new_pattern
            occurrences = new_occurrences
        else:
            pattern = new_pattern
            occurrences = new_occurrences

        # If there's still a pattern to consume
        # it means we don't have a match yet
        if not pattern:
            return match

        pos += 1
        if pos > len(text):
            break
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
