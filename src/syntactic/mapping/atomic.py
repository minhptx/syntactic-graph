import re
import string


class SubStr:
    def __init__(self, text, start_pos, end_pos):
        self.text = text
        self.end_pos = end_pos
        self.start_pos = start_pos

    def __str__(self):
        return "Substr(%s, %s, %s)" % (self.text, str(self.start_pos), str(self.end_pos))

    @staticmethod
    def generate(value_text, extraction_text):
        result = []
        position_list = []
        matches = re.finditer(re.escape(extraction_text), value_text)
        for match in matches:
            if extraction_text.isalpha():
                if match.start() == 0:
                    if match.end() < len(value_text) and value_text[match.end()].isalpha():
                        continue
                elif match.end() == len(value_text):
                    if match.start() > 0 and value_text[match.start() - 1].isalpha():
                        continue


            if extraction_text.isdigit():
                if match.start() == 0:
                    if match.end() < len(value_text) and value_text[match.end()].isdigit():
                        continue
                elif match.end() == len(value_text):
                    if match.start() > 0 and value_text[match.start() - 1].isdigit():
                        continue

            position_list.append((match.start(), match.end()))

            start_positions = Position.generate(value_text, match.start())
            end_positions = Position.generate(value_text, match.end())

            for start_pos in start_positions:
                for end_pos in end_positions:
                    result.append(SubStr(extraction_text, start_pos, end_pos))
        return result, position_list


class Position:
    def __init__(self, pre_regex, post_regex, index):
        self.pre_regex = pre_regex
        self.post_regex = post_regex
        self.index = index

    def __str__(self):
        return "Position(%s, %s, %s)" % (str(self.pre_regex), str(self.post_regex), str(self.index))

    @staticmethod
    def generate(value_text, index):
        result = []

        for k_1 in range(index - 1, index):
            if k_1 < 0:
                continue
            for k_2 in range(index + 1, index + 2):
                if k_2 > len(value_text):
                    continue

                index_match = 0
                regex = Regex.generate(value_text[k_1:k_2])
                matches = list(re.finditer(regex.to_regex(), value_text))

                num_matches = len(matches)
                for idx, match in enumerate(matches):
                    if match.start() == k_1:
                        index_match = idx
                        break

                pre_regex = Regex.generate(value_text[k_1:index])
                post_regex = Regex.generate(value_text[index:k_2])

                result.append(Position(pre_regex, post_regex, index_match + 1))
                result.append(Position(pre_regex, post_regex, -(num_matches - index_match)))
        return result


class CPos:
    def __init__(self, position):
        self.position = position

    def __str__(self):
        return "CPos(%s)" % str(self.position)


class Regex:
    NUMWRD = r"[0-9]"
    LWRD = r"[a-z]"
    UWRD = r"[A-Z]"
    PUNC = "[%s]" % (string.punctuation + "|")
    SPACE = "\s"
    TOKEN_TYPES = {"NUM": NUMWRD, "LWD": LWRD, "UWD": UWRD, "PUN": PUNC, "SPACE": SPACE}

    def __init__(self, token_seq):
        self.token_seq = token_seq

    def __str__(self):
        return "Regex(%s)" % ",".join([str(x) for x in self.token_seq])

    @staticmethod
    def generate(text):
        token_seq = []
        for letter in text:
            token = None
            for token_type, regex in Regex.TOKEN_TYPES.items():
                match = re.match(regex, "".join(letter))
                if match:
                    if token_type == "PUN":
                        token = Token(match.group(), match.group())
                    else:
                        token = Token(match.group(), token_type)
                    break
            if not token:
                token = Token(letter, "LWD")
            token_seq.append(token)
        return Regex(token_seq)

    def to_regex(self):
        regex_str = ""
        for token in self.token_seq:
            if token.type in self.TOKEN_TYPES:
                regex_str += self.TOKEN_TYPES[token.type]
            else:
                regex_str += re.escape(token.type)
        return regex_str


class Token:
    def __init__(self, text, type):
        self.text = text
        self.type = type

    def __str__(self):
        return "Token(%s)" % self.type
