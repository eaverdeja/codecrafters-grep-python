from dataclasses import dataclass
import math
import string
import sys
from typing import Any


@dataclass
class Matcher:
    pattern: str
    pos: int = 0
    occurrences: int = -1
    current_capture: str = ""
    debug: bool = False

    def match(self, text: str) -> bool:
        has_start_anchor = self.pattern.startswith("^")
        has_end_anchor = self.pattern.endswith("$")
        self.pattern = self.pattern.strip("^$")

        num_groups = self.pattern.count("(")
        alternation_text = text
        original_parentheses = self._find_matching_parentheses(self.pattern)
        parentheses_map = {
            idx + 1: (opening, closing)
            for idx, (opening, closing) in enumerate(original_parentheses)
        }
        sorted_parentheses = sorted(parentheses_map.items(), key=lambda p: p[1][1])
        for idx, _ in sorted_parentheses:
            parentheses = self._find_matching_parentheses(self.pattern)
            opening, closing = self._find_next_parentheses_pair(parentheses)
            self._debug(f"\nProcessing group [{idx}], pattern [{self.pattern}]")
            self._debug(f"Opening: [{opening}] | Closing: [{closing}]")
            if opening < self.pattern.find("|") < closing:
                match, found = self._handle_alternation(alternation_text)
                if not match:
                    return False
                alternation_text = alternation_text.replace(found, "", 1)
            if self.pattern.find(f"\\{idx}") >= 0:
                nested = False
                for p in sorted_parentheses:
                    if p[0] < idx:
                        nested = opening < p[1][1]
                offset = 0 if not nested else 1
                match = self._handle_backreference(text[opening - offset :], idx)
                if not match:
                    return False

            parentheses = self._find_matching_parentheses(self.pattern)
            opening, closing = self._find_next_parentheses_pair(parentheses)
            self.pattern = self.pattern[:opening] + self.pattern[opening + 1 :]
            self.pattern = self.pattern[: closing - 1] + self.pattern[closing:]

        if num_groups:
            self._debug("resulting pattern", self.pattern)

        if has_start_anchor:
            return self._handle_start_of_string_anchor(text, has_end_anchor)

        if has_end_anchor and not has_start_anchor:
            return self._handle_end_of_string_anchor(text)

        has_matched_once = False
        while True:
            text_at_pos = text[self.pos] if self.pos < len(text) else ""
            quantifier = self._quantifier
            match = self._match_at_pos(text_at_pos)
            if match:
                has_matched_once = True

            if quantifier and has_matched_once and not match:
                self._debug("matched once and failed! breaking")
                break

            if not self.pattern:
                return match

            self.pos += 1
            if self.pos > len(text):
                break

        return match

    def _match_at_pos(self, text: str) -> bool:
        self._debug("--- | text | pattern ")
        self._debug("---    ", text, " | ", self.pattern)
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
            elif self._quantifier:
                if self._quantifier == "+" and self.occurrences > 0:
                    self._consume_pattern(3)
                    if not self.pattern:
                        return True
                    return False
                elif self._quantifier == "?":
                    if self.occurrences == 1:
                        self._consume_pattern(3)
                self.occurrences = -1
            return match

        if self._quantifier:
            match = self._handle_quantifiers(text)
            if not match:
                if self._quantifier == "?":
                    self.pattern = self.pattern.replace(self._quantifier, "")
                self.occurrences = -1
            self.current_capture += text
            return match

        if self.pattern.startswith("."):
            self.current_capture += text
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
            if self._quantifier == "+":
                # lookahead
                if len(rest_of_pattern) > 0 and text == rest_of_pattern[0]:
                    self.pattern = rest_of_pattern[1:]
                    self.occurrences = -1
                    return True
                return self.occurrences > 0

            self.pattern = rest_of_pattern
            self._consume_pattern(1)

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
                return False

            matched_lookahead = self._handle_lookahead(text, character_class)
            if matched_lookahead is not None:
                return matched_lookahead

            self.occurrences = max(1, self.occurrences + 1)
            return True
        elif self._quantifier == "?":
            matched_lookahead = self._handle_lookahead(text, character_class)
            if matched_lookahead is not None:
                return matched_lookahead

            if match and self.occurrences == -1:
                self.occurrences = 1
                return True

            if self.occurrences == -1:
                self._consume_pattern(3)
                return True

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
                self.occurrences = -1
                return True
            if text != quantified and quantified != ".":
                if self.occurrences >= 0:
                    self.pattern = ""
                    return False
                self._consume_pattern(2)
                return False
            self.occurrences = max(1, self.occurrences + 1)
            return True
        elif self._quantifier == "?":
            # Zero or one quantifier (?)
            # Lookahead
            match = text == self.pattern[2]
            if match:
                self._consume_pattern(3)
                return True
            if text == quantified and self.occurrences == -1:
                self.occurrences = 1
                return True
            return False

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
        parentheses = self._find_matching_parentheses(self.pattern)
        opening, closing = self._find_next_parentheses_pair(parentheses)
        candidates = self.pattern[opening + 1 : closing]

        match = False
        capture = ""
        matches = []
        for candidate in candidates.split("|"):
            self._debug(f"Looking for candidate [{candidate}] in [{text}]")
            matcher = Matcher(candidate)
            did_match = matcher.match(text)
            matches.append((did_match, matcher.pos, matcher.current_capture))

        last_pos = math.inf
        for did_match, pos, current_capture in matches:
            if did_match and pos < last_pos:
                match = did_match
                capture = current_capture
                last_pos = pos

        if match:
            self._debug(f"Found match: [{capture}]")
            parentheses = self._find_matching_parentheses(self.pattern)
            opening, closing = self._find_next_parentheses_pair(parentheses)
            group = self.pattern[opening + 1 : closing]
            self.pattern = self.pattern.replace(group, capture, 1)
        return match, capture

    def _handle_backreference(self, text: str, idx: int) -> bool:
        parentheses = self._find_matching_parentheses(self.pattern)
        opening, closing = self._find_next_parentheses_pair(parentheses)
        backreference = self.pattern[opening + 1 : closing]

        matcher = Matcher(backreference)
        self._debug(f"Looking for backreference [{backreference}] in [{text}]")
        match = matcher.match(text)

        if match:
            if backreference.startswith(r"\d") or backreference.startswith(r"\w"):
                captured = matcher.current_capture
                self.pattern = self.pattern.replace(backreference, captured, 1)
                backreference = captured

            self.pattern = self.pattern.replace(f"\\{idx}", backreference, 1)
            self._debug(f"Replacing [{idx}] with [{backreference}]")
            self._debug(f"Resulting pattern: {self.pattern}")

        return match

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

    def _find_matching_parentheses(self, text: str) -> list[tuple[int, int]]:
        stack = []
        matches = []
        for i, char in enumerate(text):
            if char == "(":
                stack.append(i)
            elif char == ")":
                opening_index = stack.pop()
                matches.append((opening_index, i))

        matches.sort(key=lambda x: x[0])
        return matches

    def _find_next_parentheses_pair(
        self,
        current_parentheses: list[tuple[int, int]],
    ) -> tuple[int, int]:
        opening, closing = -sys.maxsize, sys.maxsize
        for o, c in current_parentheses:
            if c < closing:
                opening = o
                closing = c
        return opening, closing

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

    def _debug(self, *args: Any) -> None:
        if self.debug:
            print(*args)
