import regex as re


class Atomic(object):
    def __init__(self, name, regex, abbr):
        self.name = name
        self.regex = regex
        self.abbr = abbr

    def __eq__(self, other):
        if not other:
            return False
        return self.name == other.name and self.regex == other.regex and self.abbr == other.abbr

    def is_subset(self, other_atomic):
        pass


class ProperCase(Atomic):
    def __init__(self):
        super(ProperCase, self).__init__("ProperCase", r"\p{Lt}+", "Pp")

    def is_subset(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, PROPER_CASE_WS]:
            return True
        else:
            return False

    def is_transformable_from(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, PROPER_CASE_WS]:
            return
        else:
            return False


class UpperCase(Atomic):
    def __init__(self):
        super(UpperCase, self).__init__("Uppercase", r"\p{Lu}+", "U")

    def is_subset(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, UPPER_CASE_WS]:
            return True
        else:
            return False

    def is_transformable_from(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, PROPER_CASE_WS]:
            return True
        else:
            return False


class LowerCase(Atomic):
    def __init__(self):
        super(LowerCase, self).__init__("LowerCase", r"\p{Ll}+", "l")

    def is_subset(self, atomic):
        if atomic in [ALPHABET, ALPHANUM, ALPHABET_WS, LOWER_CASE_WS]:
            return True
        else:
            return False


class Digit(Atomic):
    def __init__(self):
        super(Digit, self).__init__("Digit", r"\p{N}+", "d")

    def is_subset(self, atomic):
        if atomic in [ALPHANUM]:
            return True
        else:
            return False


class Alphabet(Atomic):
    def __init__(self):
        super(Alphabet, self).__init__("Alphabet", r"\p{L}+", "a")

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
        super(Whitespace, self).__init__("Whitespace", r"\p{Z}+", "s")

    def is_subset(self, atomic):
        if atomic in [UPPER_CASE_WS, LOWER_CASE_WS, PROPER_CASE_WS, ALPHABET_WS]:
            return True
        else:
            return False


class Punctuation(Atomic):
    def __init__(self):
        super(Punctuation, self).__init__("Punctuation", r"(\p{P}|\p{S})+", ".")


class StartToken(Atomic):
    def __init__(self):
        super(StartToken, self).__init__("StartToken", "^", "^")


class EndToken(Atomic):
    def __init__(self):
        super(EndToken, self).__init__('EndToken', "$", "$")


class ProperCaseWhitespace(Atomic):
    def __init__(self):
        super(ProperCaseWhitespace, self).__init__(
            "ProperCaseWhitespace", r"\p{Lt}+(\p{Z}+\p{L}+)*", "ps")

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS]:
            return True
        else:
            return False


class UpperCaseWhitespace(Atomic):
    def __init__(self):
        super(UpperCaseWhitespace, self).__init__(
            "UpperCaseWhitespace", r"\p{Lu}+(\p{Z}+\p{Lu}+)*", "Cs")

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS]:
            return True
        else:
            return False


class LowerCaseWhitespace(Atomic):
    def __init__(self):
        super(LowerCaseWhitespace, self).__init__(
            "LowerCaseWhitespace", r"\p{Ll}+(\p{Z}+\p{Ll}+)*", "ls")

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS]:
            return True
        else:
            return False


class AlphabetPunctuation(Atomic):
    def __init__(self):
        super(AlphabetPunctuation, self).__init__(
            "AlphabetPunctuation", r"(\p{P}|\p{S}|\p{L}|\s)+", "ap")

    def is_subset(self, atomic):
        if atomic in [ALPHA_PUNC]:
            return True
        else:
            return False


class Any(Atomic):
    def __init__(self):
        super(Any, self).__init__("AlphabetPunctuation", r".+", "any")

    def is_subset(self, atomic):
        if atomic in [ANY]:
            return True
        else:
            return False


class AlphabetWhitespace(Atomic):
    def __init__(self):
        super(AlphabetWhitespace, self).__init__(
            "AlphabetWhitespace", r"\p{L}+(\p{Z}+\p{L}+)*", "as")

    def is_subset(self, atomic):
        if atomic in [ALPHABET_WS, ALPHA_PUNC]:
            return True
        else:
            return False


class ConstantString(Atomic):
    def __init__(self, text):
        super(ConstantString, self).__init__("ConstantString", re.escape(text), "cs")

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
ALPHA_PUNC = AlphabetPunctuation()
ANY = Any()

ATOMIC_LIST = [PROPER_CASE, UPPER_CASE, LOWER_CASE, DIGIT, ALPHABET, ALPHANUM, WHITESPACE, PROPER_CASE_WS,
               LOWER_CASE_WS, UPPER_CASE_WS, ALPHABET_WS, PUNCTUATION, ALPHA_PUNC, ANY]

if __name__ == "__main__":
    a = ConstantString("33")
    b = ConstantString("33")

    assert a == b
