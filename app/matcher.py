from dataclasses import dataclass
import string


@dataclass
class Matcher:
    pattern: str
    pos: int = 0
    occurrences: int = -1
    current_capture: str = ""

    def match(self, text: str) -> bool:
        # Keep track of anchors
        has_start_anchor = self.pattern.startswith("^")
        has_end_anchor = self.pattern.endswith("$")

        # And strip them for processing
        self.pattern = self.pattern.strip("^$")

        if has_start_anchor:
            return self._handle_start_of_string_anchor(text, has_end_anchor)

        if has_end_anchor and not has_start_anchor:
            return self._handle_end_of_string_anchor(text)

        num_groups = self.pattern.count("(")
        capture_text = text
        for i in range(1, num_groups + 1):
            opening = self.pattern.find("(")
            closing = self.pattern.find(")")
            if opening >= 0 and closing:
                if opening < self.pattern.find("|") < closing:
                    match, found = self._handle_alternation(text)
                    if not match:
                        return False
                    text = text.replace(found, "")
                else:
                    match, capture = self._handle_backreference(capture_text, i)
                    print("capture", capture)
                    if not match:
                        return False
                    capture_text = capture_text.replace(capture, "").strip()

        print("resulting pattern", self.pattern)

        has_matched_once = False
        while True:
            quantifier = self._quantifier
            text_at_pos = text[self.pos] if self.pos < len(text) else ""
            match = self._match_at_pos(text_at_pos)
            if match:
                has_matched_once = True

            if has_matched_once and not match and not quantifier:
                print("matched once and failed! breaking")
                break
            if quantifier and not match:
                self.pattern = self.pattern.replace(quantifier, "")

            if not self.pattern:
                return match

            self.pos += 1
            if self.pos > len(text):
                break

        return match

    def _match_at_pos(self, text: str) -> bool:
        print("--- | text | pattern ")
        print("---    ", text, " | ", self.pattern)
        if not text:
            return self._handle_empty_text()

        if self.pattern.startswith("[") and self.pattern.find("]"):
            return self._handle_character_groups(text)

        if self.pattern.startswith(r"\d") or self.pattern.startswith(r"\w"):
            match = self._handle_character_classes(text)
            if match:
                if self._quantifier and self.occurrences >= 0:
                    self.current_capture += text
                elif not self._quantifier:
                    self.current_capture += text
            return match

        if self._quantifier:
            return self._handle_quantifiers(text)

        if self.pattern.startswith("."):
            return self._handle_wildcard()

        # Literal character
        match = text == self.pattern[0] if self.pattern else False
        if match:
            self._consume_pattern(1)
            self.current_capture += text
            return True

        return False

    def _handle_empty_text(self) -> bool:
        if self.pattern == "":
            return True
        if self.pattern.endswith("?"):
            self._consume_pattern(2)
            return True
        elif self.pattern.endswith("+"):
            self._consume_pattern(2)
            return self.occurrences > 0
        return False

    def _handle_character_groups(self, text: str) -> bool:
        offset = 2 if self._quantifier else 1
        rest_of_pattern = self.pattern[self.pattern.index("]") + offset :]

        chars = self.pattern[self.pattern.index("[") + 1 : self.pattern.index("]")]
        if chars.startswith("^"):
            # Negative characters group
            chars = chars.strip("^")
            match = text not in chars
        else:
            # Positive character group
            match = text in chars

        if match:
            if self._quantifier == "+":
                self.occurrences += 1
            else:
                self.pattern = rest_of_pattern
            return True
        else:
            self.pattern = rest_of_pattern
            self._consume_pattern(1)
            if self.occurrences > 0:
                self.occurrences = -1
                return True

        self.pattern = ""
        return False

    def _handle_character_classes(self, text: str) -> bool:
        is_digit = self.pattern.startswith(r"\d")
        valid_chars = (
            string.digits if is_digit else (string.digits + string.ascii_letters)
        )
        character_class = r"\d" if is_digit else r"\w"
        match = text in valid_chars

        if self._quantifier == "+":
            if not match:
                self.occurrences = -1
                return False

            matched_lookahead = self._handle_lookahead(text, character_class)
            if matched_lookahead is not None:
                return matched_lookahead

            self.occurrences = max(1, self.occurrences + 1)
            return True
        elif self._quantifier == "?":
            if match:
                self.occurrences = 1

                matched_lookahead = self._handle_lookahead(text, character_class)
                if matched_lookahead is not None:
                    return matched_lookahead

                return True

            if self.occurrences == -1:
                self.pattern = self.pattern.replace(character_class, "", 1).replace(
                    "?", "", 1
                )
                return True
            self.occurrences = 0
            return False

        if match:
            self.pattern = self.pattern.replace(character_class, "", 1)
            return True
        return False

    def _handle_quantifiers(self, text: str) -> bool:
        quantified = self.pattern[0]
        if self._quantifier == "+":
            # One or more quantifier (+)
            # Lookahead
            if text == self.pattern[2] and self.occurrences > 0:
                self._consume_pattern(3)
                return True
            if text != quantified and quantified != ".":
                if self.occurrences >= 0:
                    self.pattern = ""
                    return False
                self.occurrences = -1
                self._consume_pattern(2)
                return False
            self.occurrences = max(1, self.occurrences + 1)
            return True
        elif self._quantifier == "?":
            # Zero or more quantifier (?)
            # Lookahead
            match = text == self.pattern[2]
            if match:
                self._consume_pattern(3)
                return True
            if text == quantified:
                self.occurrences = 1
                # self._consume_pattern(2)
                return True
            self.occurrences = 0

            return match

        raise ValueError("Expected quantifier to be present")

    def _handle_start_of_string_anchor(self, text: str, has_end_anchor: bool) -> bool:
        for i in range(len(self.pattern)):
            match = self._match_at_pos(text[i])
            if not match:
                return False
        if not has_end_anchor:
            return True
        return match and i + 1 == len(text)

    def _handle_end_of_string_anchor(self, text: str) -> bool:
        # Flip things around if there's just an end anchor
        if len(text) < len(self.pattern):
            return False
        end_portion = text[-len(self.pattern) :]
        return Matcher(f"^{self.pattern}").match(end_portion)

    def _handle_alternation(self, text: str) -> tuple[bool, str]:
        candidates = self.pattern[self.pattern.index("(") + 1 : self.pattern.index(")")]

        match = False
        for candidate in candidates.split("|"):
            match = Matcher(candidate).match(text)
            if match:
                break

        if match:
            self.pattern = (
                self.pattern[: self.pattern.find("(")]
                + self.pattern[self.pattern.find(")") + 1 :]
            )
        return match, candidate

    def _handle_backreference(self, text: str, idx: int) -> tuple[bool, str]:
        backreference = self.pattern[
            self.pattern.index("(") + 1 : self.pattern.index(")")
        ]

        matcher = Matcher(backreference)
        print(f"Looking for {backreference} in {text}")
        match = matcher.match(text)

        if match:
            if backreference.startswith(r"\d") or backreference.startswith(r"\w"):
                captured = matcher.current_capture
                self.pattern = self.pattern.replace(backreference, captured)
                backreference = captured

            self.pattern = self.pattern.replace(f"\\{idx}", backreference)
            self.pattern = self.pattern.replace("(", "", 1).replace(")", "", 1)

        return match, matcher.current_capture

    def _handle_wildcard(self) -> bool:
        # Anything goes!
        self.pattern = self.pattern[1:]
        return True

    def _handle_lookahead(self, text: str, character_class: str) -> bool | None:
        quantifier = self._quantifier
        if not quantifier:
            return None

        lookahead = (
            self.pattern[self.pattern.index(quantifier) + 1]
            if len(self.pattern) > self.pattern.index(quantifier) + 1
            else None
        )
        if text == lookahead:
            self.pattern = self.pattern.replace(character_class, "", 1).replace(
                quantifier, "", 1
            )
            return self._match_at_pos(text)
        return None

    def _consume_pattern(self, n: int) -> None:
        self.pattern = self.pattern[n:]

    @property
    def _quantifier(self) -> str | None:
        pattern = self.pattern
        if pattern.startswith(r"\d") or pattern.startswith(r"\w"):
            # There's an extra backslash used to escape in this case, remove it
            pattern = pattern[1:]
        if pattern.startswith("["):
            quantifier_idx = pattern.index("]") + 1
            return (
                pattern[quantifier_idx]
                if len(pattern) > quantifier_idx
                and pattern[quantifier_idx] in ("+", "?")
                else None
            )
        return pattern[1] if len(pattern) > 1 and pattern[1] in ("+", "?") else None
