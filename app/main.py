import sys

from app.matcher import Matcher

# import pyparsing - available if you need it!
# import lark - available if you need it!


def main():
    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    pattern = sys.argv[2]
    text = sys.stdin.read()

    match = Matcher(pattern).match(text)

    if not match:
        print("not found!")
        exit(1)
    else:
        print("found!")
        exit(0)


if __name__ == "__main__":
    main()
