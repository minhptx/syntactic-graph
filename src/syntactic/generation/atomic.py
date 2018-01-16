import regex as re

class Atomic(object):
    def __init__(self, name, regex, abbr):
        self.name = name
        self.regex = regex
        self.abbr = abbr


class ProperCase(Atomic):
    def __init__(self):
        super(ProperCase, self).__init__("ProperCase", "[A-Z][a-z]+", "Pp")


class UpperCase(Atomic):
    def __init__(self):
        super(UpperCase, self).__init__("Uppercase", "[A-Z]+", "U")


class LowerCase(Atomic):
    def __init__(self):
        super(LowerCase, self).__init__("LowerCase", "[a-z]+", "l")


class Digit(Atomic):
    def __init__(self):
        super(Digit, self).__init__("Digit", r"\d+", "d")


class Alphabet(Atomic):
    def __init__(self):
        super(Alphabet, self).__init__("Alphabet", r"[A=Za=z]+", "a")


class Alphanumeric(Atomic):
    def __init__(self):
        super(Alphanumeric, self).__init__(
            "Alphanumeric", r"[A-Za-z0-9]+", "a0")


class Whitespace(Atomic):
    def __init__(self):
        super(Whitespace, self).__init__("Whitespace", r"\s+", "s")

class Punctuation(Atomic):
    def __init__(self):
        super(Punctuation, self).__init__("Punctuation", ur"(\p{P}|\p{S})+", ".")


class StartToken(Atomic):
    def __init__(self):
        super(StartToken, self).__init__("StartToken", "^", "^")


class EndToken(Atomic):
    def __init__(self):
        super(EndToken, self).__init__('EndToken', "$", "$")


class ProperCaseWhitespace(Atomic):
    def __init__(self):
        super(ProperCaseWhitespace, self).__init__(
            "ProperCaseWhitespace", r"[A-Z][a-z]+(\s+[A-Z][a-z]+)*", "ps")


class UpperCaseWhitespace(Atomic):
    def __init__(self):
        super(UpperCaseWhitespace, self).__init__(
            "UpperCaseWhitespace", r"[A-Z]+(\s+[A-Z]+)*", "Cs")


class LowerCaseWhitespace(Atomic):
    def __init__(self):
        super(LowerCaseWhitespace, self).__init__(
            "LowerCaseWhitespace", r"[a-z]+(\s+[a-z]+)*", "ls")


class AlphabetWhitespace(Atomic):
    def __init__(self):
        super(AlphabetWhitespace, self).__init__(
            "AlphabetWhitespace", r"[A-Za-z]+(\s+[A-Za-z]+)*", "as")


class ConstantString(Atomic):
    def __init__(self, text):
        super(ConstantString, self).__init__("ConstantString(%s)" % text, re.escape(text), "cs")


PROPER_CASE = ProperCase()
UPPER_CASE = UpperCase()
LOWER_CASE = LowerCase()
DIGIT = Digit()
ALPHABET = Alphabet()
ALPHANUM = Alphanumeric()
WHITESPACE = Whitespace()
START_TOKEN = StartToken()
END_TOKEN = EndToken()
PROPER_CASE_WS = ProperCaseWhitespace()
UPPER_CASE_WS = UpperCaseWhitespace()
LOWER_CASE_WS = LowerCaseWhitespace()
ALPHABET_WS = AlphabetWhitespace()
PUNCTUATION = Punctuation()

ATOMIC_LIST = [PROPER_CASE, UPPER_CASE, LOWER_CASE, DIGIT, ALPHABET, ALPHANUM, WHITESPACE, PROPER_CASE_WS, LOWER_CASE_WS,
               UPPER_CASE_WS, ALPHABET_WS, PUNCTUATION]
