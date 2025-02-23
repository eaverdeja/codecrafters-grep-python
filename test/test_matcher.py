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
            # # Zero or one quantifier
            ("cat", "ca?t", True),
            ("act", "ca?t", True),
            ("a caat", "ca?t", False),
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
            ("caaat", r"c\w?t", False),
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
            ("a dog and cats", "a (cat|dog) and (cat|dog)s", True),
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
            (
                "this starts and ends with this",
                r"^(\w+) starts and ends with \1$",
                True,
            ),
            (
                "once a dreaaamer, alwayszzz a dreaaamer",
                "once a (drea+mer), alwaysz? a \1",
                False,
            ),
            ("bugs here and bugs there", r"(b..s|c..e) here and \1 there", True),
            ("bugz here and bugs there", r"(b..s|c..e) here and \1 there", False),
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
            (
                "abc-def is abc-def, not efg",
                r"([abc]+)-([def]+) is \1-\2, not [^xyz]+",
                True,
            ),
            ("apple pie, apple and pie", r"^(\w+) (\w+), \1 and \2$", True),
            ("howwdy hey there, howwdy hey", r"(how+dy) (he?y) there, \1 \2", True),
            #
            # # Nested backreferences
            (
                "'cat and cat' is the same as 'cat and cat'",
                r"('(cat) and \2') is the same as \1",
                True,
            ),
            (
                "grep 101 is doing grep 101 times, and again grep 101 times",
                r"((\w\w\w\w) (\d\d\d)) is doing \2 \3 times, and again \1 times",
                True,
            ),
            (
                "'howwdy hey there' is made up of 'howwdy' and 'hey'. howwdy hey there",
                r"'((how+dy) (he?y) there)' is made up of '\2' and '\3'. \1",
                True,
            ),
            (
                "howwdy heeey there, howwdy heeey",
                r"(how+dy) (he?y) there, \1 \2",
                False,
            ),
            (
                "cat and fish, cat with fish, cat and fish",
                r"((c.t|d.g) and (f..h|b..d)), \2 with \3, \1",
                True,
            ),
            (
                "bat and fish, bat with fish, bat and fish",
                r"((c.t|d.g) and (f..h|b..d)), \2 with \3, \1",
                False,
            ),
        ],
    )
    def test_matches(self, text, pattern, is_match):
        assert Matcher(pattern).match(text) is is_match
