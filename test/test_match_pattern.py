import pytest

from app.main import match_pattern


class TestMatchPattern:
    class TestZeroOrMoreTimes:
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
            ],
        )
        def test_matches(self, text, pattern, is_match):
            assert match_pattern(text, pattern) is is_match
