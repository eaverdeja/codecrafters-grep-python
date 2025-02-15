import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


def _match_at_pos(
    text: str, pattern: str, quantifier: str | None, occurrences: int
) -> tuple[bool, str, int]:
    if not text:
        if not pattern:
            return True, "", occurrences
        if pattern.endswith("?"):
            return True, pattern[2:], occurrences
        elif pattern.endswith("+"):
            return occurrences >= 0, pattern[2:], occurrences
        return False, pattern, occurrences

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

    if pattern.find("[") >= 0 and pattern.find("]"):
        # Character groups
        rest_of_pattern = pattern[pattern.index("]") + 1 :]

        chars = pattern[pattern.index("[") + 1 : pattern.index("]")]
        if chars.startswith("^"):
            # Negative characters group
            chars = chars.strip("^")
            match = text not in chars
        else:
            # Positive character group
            match = text in chars
        return (
            (True, rest_of_pattern, occurrences) if match else (False, "", occurrences)
        )

    # Character classes
    if pattern.startswith(r"\d") or pattern.startswith(r"\w"):
        is_digit = pattern.startswith(r"\d")
        valid_chars = (
            string.digits if is_digit else (string.digits + string.ascii_letters)
        )
        character_class = r"\d" if is_digit else r"\w"
        match = text in valid_chars

        if quantifier == "+":
            if not match:
                if occurrences > 0:
                    return True, pattern.replace(character_class, ""), -1
                return False, pattern, -1
            occurrences = max(1, occurrences + 1)
            return True, pattern, occurrences
        elif quantifier == "?":
            if match:
                return True, pattern.replace(character_class, "", 1), 1
            return True, pattern.replace(character_class, "", 1), 0

        if match:
            return True, pattern.replace(character_class, "", 1), occurrences
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

    # Keep track of anchors
    has_start_anchor = pattern.startswith("^")
    has_end_anchor = pattern.endswith("$")

    # And strip them for processing
    pattern = pattern.strip("^$")

    if has_start_anchor:
        for i in range(len(pattern)):
            if i >= len(text):
                return False

            quantifier = _get_quantifier(pattern)
            match, new_pattern, new_occurrences = _match_at_pos(
                text[i], pattern[i:], quantifier, occurrences
            )
            if not match:
                return False
        if not has_end_anchor:
            return True
        return len(text) == len(pattern)

    # Flip things around if there's just an end anchor
    if has_end_anchor and not has_start_anchor:
        if len(text) < len(pattern):
            return False
        end_portion = text[-len(pattern) :]
        return match_pattern(end_portion, f"^{pattern}")

    while True:
        try:
            text_at_pos = text[pos]
        except IndexError:
            text_at_pos = ""

        quantifier = _get_quantifier(pattern)
        match, new_pattern, new_occurrences = _match_at_pos(
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


def _get_quantifier(pattern: str) -> str | None:
    if pattern.startswith(r"\d") or pattern.startswith(r"\w"):
        # There's an extra backslash used to escape in this case, remove it
        pattern = pattern[1:]
    return pattern[1] if len(pattern) > 1 and pattern[1] in ("+", "?") else None


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
