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
        ],
    )
    def test_matches(self, text, pattern, is_match):
        assert Matcher(pattern).match(text) is is_match
