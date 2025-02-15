from dataclasses import dataclass
import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!

MatchResult = tuple[bool, str]


@dataclass
class Matcher:
    pos: int = 0
    occurrences: int = -1

    def _match_at_pos(
        self, text: str, pattern: str, quantifier: str | None
    ) -> MatchResult:
        print(f"\ntext: {text} | pattern: {pattern} | quantifier: {quantifier}")
        if not text:
            return self._handle_empty_text(pattern)

        if pattern.startswith("^"):
            return self._handle_start_of_string_anchor(text, pattern)

        if pattern.startswith("[") and pattern.find("]"):
            return self._handle_character_groups(text, pattern)

        if pattern.startswith(r"\d") or pattern.startswith(r"\w"):
            return self._handle_character_classes(text, pattern, quantifier)

        if quantifier:
            return self._handle_quantifiers(text, pattern, quantifier)

        # Literal character
        match = text == pattern[0] if pattern else False
        return (True, pattern[1:]) if match else (False, pattern)

    def _handle_empty_text(self, pattern: str) -> MatchResult:
        if not pattern:
            return True, ""
        if pattern.endswith("?"):
            return True, pattern[2:]
        elif pattern.endswith("+"):
            return self.occurrences >= 0, pattern[2:]
        return False, pattern

    def _handle_start_of_string_anchor(self, text: str, pattern: str) -> MatchResult:
        pattern = pattern.lstrip("^")
        # Literal match
        match = text == pattern[0]
        if match:
            return True, pattern[1:]
        # If there's no match at the start, then short-circuit
        # the operation by returning an empty pattern
        return False, ""

    def _handle_character_groups(self, text: str, pattern: str) -> MatchResult:
        rest_of_pattern = pattern[pattern.index("]") + 1 :]

        chars = pattern[pattern.index("[") + 1 : pattern.index("]")]
        if chars.startswith("^"):
            # Negative characters group
            chars = chars.strip("^")
            match = text not in chars
        else:
            # Positive character group
            match = text in chars
        return (True, rest_of_pattern) if match else (False, "")

    def _handle_character_classes(
        self, text: str, pattern: str, quantifier: str | None
    ) -> MatchResult:
        is_digit = pattern.startswith(r"\d")
        valid_chars = (
            string.digits if is_digit else (string.digits + string.ascii_letters)
        )
        character_class = r"\d" if is_digit else r"\w"
        match = text in valid_chars

        if quantifier == "+":
            if not match:
                self.occurrences = -1
                if self.occurrences > 0:
                    return True, pattern.replace(character_class, "")
                return False, pattern
            self.occurrences = max(1, self.occurrences + 1)
            return True, pattern
        elif quantifier == "?":
            if match:
                self.occurrences = 1
                return True, pattern.replace(character_class, "", 1)
            self.occurrences = 0
            return True, pattern.replace(character_class, "", 1)

        if match:
            return True, pattern.replace(character_class, "", 1)
        return False, pattern

    def _handle_quantifiers(
        self, text: str, pattern: str, quantifier: str | None
    ) -> MatchResult:
        quantified = pattern[0]
        if quantifier == "+":
            # One or more quantifier (+)
            if not text == quantified:
                if self.occurrences >= 0:

                    return (True, pattern[3:]) if text == pattern[2] else (False, "")
                self.occurrences = -1
                return False, pattern[1:]
            self.occurrences = max(1, self.occurrences + 1)
            return True, pattern
        elif quantifier == "?":
            # Zero or more quantifier (?)
            if text == quantified:
                self.occurrences = 1
                return True, pattern[2:]
            self.occurrences = 0
            return text == pattern[2], pattern[3:]
        else:
            raise ValueError(f"Unsupported quantifier: {quantifier}")

    def match_pattern(self, text: str, pattern: str) -> bool:
        # Keep track of anchors
        has_start_anchor = pattern.startswith("^")
        has_end_anchor = pattern.endswith("$")

        # And strip them for processing
        pattern = pattern.strip("^$")

        if has_start_anchor:
            for i in range(len(pattern)):
                if i >= len(text):
                    return False

                quantifier = self._get_quantifier(pattern)
                match, new_pattern = self._match_at_pos(
                    text[i], pattern[i:], quantifier
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
            return self.match_pattern(end_portion, f"^{pattern}")

        while True:
            text_at_pos = text[self.pos] if self.pos < len(text) else ""

            quantifier = self._get_quantifier(pattern)
            match, new_pattern = self._match_at_pos(text_at_pos, pattern, quantifier)
            print(match)

            # If we're counting the optional quantifier,
            # we can't consume our input string or else
            # we won't be able to check for the empty case
            if quantifier == "?" and new_pattern == pattern:
                continue

            pattern = new_pattern
            # If there's still a pattern to consume
            # it means we don't have a match yet
            if not pattern:
                return match

            self.pos += 1
            if self.pos > len(text):
                break
        return match

    def _get_quantifier(self, pattern: str) -> str | None:
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

    match = Matcher().match_pattern(text, pattern)

    if not match:
        print("not found!")
        exit(1)
    else:
        print("found!")
        exit(0)


if __name__ == "__main__":
    main()
