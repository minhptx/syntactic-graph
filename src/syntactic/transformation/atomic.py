import regex as re


class Select:
    def __init__(self, position, start_pos, end_pos, length):
        self.position = position
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __str__(self):
        return "Select(%s, %s, %s)" % (self.position, str(self.start_pos), str(self.end_pos))

    @staticmethod
    def generate(raw_path, tranformed_path):
        result = []
        position_list = []
        matches = []

        for edge_1 in raw_path:
            for edge_2 in tranformed_path:
                if edge_1.is_subset(edge_2):
                    matches.append(edge_1)
        
        for match in matches:
            # print(match.start(), match.end(), len(value_text), extraction_text, value_text)
            if tranformed_path.isalpha():
                if match.start() == 0:
                    if match.end() < len(raw_path) and raw_path[match.end()].isalpha():
                        continue
                elif match.end() == len(raw_path):
                    if match.start() > 0 and raw_path[match.start() - 1].isalpha():
                        continue
                elif raw_path[match.start() - 1].isalpha() or raw_path[match.end()].isalpha():
                    continue

            if tranformed_path.isdigit():
                if match.start() == 0:
                    if match.end() < len(raw_path) and raw_path[match.end()].isdigit():
                        continue
                elif match.end() == len(raw_path):
                    if match.start() > 0 and raw_path[match.start() - 1].isdigit():
                        continue
                elif raw_path[match.start() - 1].isdigit() and raw_path[match.end()].isdigit():
                    continue

            position_list.append((match.start(), match.end()))

            start_positions = Position.generate(raw_path, match.start())
            end_positions = Position.generate(raw_path, match.end())

            for start_pos in start_positions:
                for end_pos in end_positions:
                    result.append(Select(tranformed_path, start_pos, end_pos))
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

        for k_1 in range(0, index):
            for k_2 in range(index + 1, len(value_text)):

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
    PUNC = ur"\p{P}"
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
