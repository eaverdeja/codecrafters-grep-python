import pytest

from app.matcher import Matcher


class TestMatch:
    @pytest.mark.parametrize(
        "text, pattern, is_match",
        [
            #
            # # Basic literal matches
            ("hello", "hello", True),
            ("hello world", "world", True),
            ("hello", "world", False),
            #
            # # Start of string anchor (^)
            ("cat", "^cat", True),
            ("scatter", "^cat", False),
            ("the cat", "^cat", False),
            ("ct", "^cat", False),
            #
            # # End of string anchor ($)
            ("cat", "cat$", True),
            ("dogdogdog", "dog$", True),
            ("the cat", "cat$", True),
            ("ct", "cat$", False),
            ("cats", "cat$", False),
            #
            # # Both anchors
            ("cat", "^cat$", True),
            ("cats", "^cat$", False),
            ("the cat", "^cat$", False),
            #
            # # Zero or more quantifier
            ("cat", "ca?t", True),
            ("act", "ca?t", True),
            ("a caat", "ca?t", True),
            ("cbt", "ca?t", False),
            ("dog", "ca?t", False),
            ("cag", "ca?t", False),
            #
            # # One or more quantifier
            ("caaats", "ca+ts", True),
            ("cat", "ca+t", True),
            ("caabats", "ca+ts", False),
            ("act", "ca+t", False),
            ("ca", "ca+t", False),
            #
            # # Character classes (\d, \w)
            ("a1b", r"\d", True),
            ("abc", r"\d", False),
            ("abc", r"\d+", False),
            ("123", r"\d+", True),
            ("a1b", r"\d+", True),
            ("a1b", r"\d?", True),
            ("0", r"\d?", True),
            ("a1b", r"\w+", True),
            ("!@#", r"\w", False),
            ("!@#", r"\w?", True),
            ("cat", r"c\w?t", True),
            ("caaat", r"c\w+t", True),
            ("caa?t", r"c\w+t", False),
            ("caaat", r"c\w?t", True),
            ("caaa!t", r"c\w?t", False),
            #
            # # Character groups []
            ("a", "[abcd]", True),
            ("cat", "[cd]at", True),
            ("dat", "[cd]at", True),
            ("bat", "[cd]at", False),
            ("cat", "[^cd]at", False),
            ("bat", "[^cd]at", True),
            ("abcd", "[abcd]+", True),
            #
            # # Wildcards (.)
            ("cat", "c.t", True),
            ("goøö0Ogol", "g.+gol", True),
            ("car", "c.t", False),
            ("gol", "g.+gol", False),
            #
            # # Alternation (|)
            ("cat", "(cat|dog)", True),
            ("dog", "(cat|dog)", True),
            ("duck", "(cat|dog)", False),
            ("a cat", "a (cat|dog)", True),
            ("one dog", "a (cat|dog)", False),
            ("dog and cats", "(dog|cat) and (dog|cat)s", True),
            #
            # # Backreferences
            ("cat and cat", r"(cat) and \1", True),
            ("cat and cat", r"(\w+) and \1", True),
            ("dog and dog", r"(\w+) and \1", True),
            ("cat and dog", r"(cat) and \1", False),
            ("cat and dog", r"(\w+) and \1", False),
            ("abcd is abcd", r"([abcd]+) is \1", True),
            ("abcd is abcd, not efg", r"([abcd]+) is \1, not [^xyz]+", True),
            ("abcd is abcd, not xyz", r"([abcd]+) is \1, not [^xyz]+", False),
            (
                "grep 101 is doing grep 101 times",
                r"(\w\w\w\w \d\d\d) is doing \1 times",
                True,
            ),
            (
                "$?! 101 is doing $?! 101 times",
                r"(\w\w\w \d\d\d) is doing \1 times",
                False,
            ),
            #
            # # Multiple backreferences
            (
                "3 red squares and 3 red circles",
                r"(\d+) (\w+) squares and \1 \2 circles",
                True,
            ),
            (
                "3 red squares and 4 red circles",
                r"(\d+) (\w+) squares and \1 \2 circles",
                False,
            ),
        ],
    )
    def test_matches(self, text, pattern, is_match):
        assert Matcher(pattern).match(text) is is_match
