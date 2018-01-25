import regex as re


class Atomic(object):
    def __init__(self, name, regex, abbr):
        self.name = name
        self.regex = regex
        self.abbr = abbr

    def __eq__(self, other):
        return self.name == other.name and self.regex == other.regex and self.abbr == other.abbr

    def is_subset(self, other_atomic):
        pass


class ProperCase(Atomic):
    def __init__(self):
        super(ProperCase, self).__init__("ProperCase", "[A-Z][a-z]+", "Pp")

    def is_subset(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, PROPER_CASE_WS]:
            return True
        else:
            return False


class UpperCase(Atomic):
    def __init__(self):
        super(UpperCase, self).__init__("Uppercase", "[A-Z]+", "U")

    def is_subset(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, UPPER_CASE_WS]:
            return True
        else:
            return False


class LowerCase(Atomic):
    def __init__(self):
        super(LowerCase, self).__init__("LowerCase", "[a-z]+", "l")

    def is_subset(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, LOWER_CASE_WS]:
            return True
        else:
            return False


class Digit(Atomic):
    def __init__(self):
        super(Digit, self).__init__("Digit", r"\d+", "d")

    def is_subset(self, atomic):
        if atomic in [ALPHANUM]:
            return True
        else:
            return False


class Alphabet(Atomic):
    def __init__(self):
        super(Alphabet, self).__init__("Alphabet", r"[A-Za-z]+", "a")

    def is_subset(self, atomic):
        if atomic in [ALPHANUM, ALPHABET_WS]:
            return True
        else:
            return False


class Alphanumeric(Atomic):
    def __init__(self):
        super(Alphanumeric, self).__init__(
            "Alphanumeric", r"[A-Za-z0-9]+", "a0")


class Whitespace(Atomic):
    def __init__(self):
        super(Whitespace, self).__init__("Whitespace", r"\s+", "s")

    def is_subset(self, atomic):
        if atomic in [UPPER_CASE_WS, LOWER_CASE_WS, PROPER_CASE_WS, ALPHABET_WS]:
            return True
        else:
            return False


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

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS]:
            return True
        else:
            return False


class UpperCaseWhitespace(Atomic):
    def __init__(self):
        super(UpperCaseWhitespace, self).__init__(
            "UpperCaseWhitespace", r"[A-Z]+(\s+[A-Z]+)*", "Cs")

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS]:
            return True
        else:
            return False


class LowerCaseWhitespace(Atomic):
    def __init__(self):
        super(LowerCaseWhitespace, self).__init__(
            "LowerCaseWhitespace", r"[a-z]+(\s+[a-z]+)*", "ls")

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS]:
            return True
        else:
            return False


class AlphabetWhitespace(Atomic):
    def __init__(self):
        super(AlphabetWhitespace, self).__init__(
            "AlphabetWhitespace", r"[A-Za-z]+(\s+[A-Za-z]+)*", "as")

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS]:
            return True
        else:
            return False


class ConstantString(Atomic):
    def __init__(self, text):
        super(ConstantString, self).__init__("ConstantString(%s)" % text, re.escape(text), "cs")

    def is_subset(self, atomic):
        if re.match(atomic.regex, self.regex):
            return True
        else:
            return False


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

ATOMIC_LIST = [PROPER_CASE, UPPER_CASE, LOWER_CASE, DIGIT, ALPHABET, ALPHANUM, WHITESPACE, PROPER_CASE_WS,
               LOWER_CASE_WS, UPPER_CASE_WS, ALPHABET_WS, PUNCTUATION]
