import pytest

from app.main import match_pattern


class TestMatchPattern:
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
            #
            # # End of string anchor ($)
            ("cat", "cat$", True),
            ("dogdogdog", "dog$", True),
            ("the cat", "cat$", True),
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
            ("act", "ca+t", False),
            ("ca", "ca+t", False),
            #
            # # Character classes (\d, \w)
            ("a1b", r"\d", True),
            ("abc", r"\d", False),
            ("123", r"\d+", True),
            ("a1b", r"\w+", True),
            ("!@#", r"\w", False),
            ("!@#", r"\w?", True),
            #
            # # Character groups []
            ("a", "[abcd]", True),
            ("cat", "[cd]at", True),
            ("dat", "[cd]at", True),
            ("bat", "[cd]at", False),
            ("cat", "[^cd]at", False),
            ("bat", "[^cd]at", True),
        ],
    )
    def test_matches(self, text, pattern, is_match):
        assert match_pattern(text, pattern) is is_match
