class Feature:
    def __init__(self, pattern_token, pre_token, post_token):
        self.pattern_token = pattern_token
        self.pre_token = pre_token
        self.post_token = post_token

    def token_to_value(self):
        return 0


class FeatureGenerator:
    def __init__(self, pattern_token, pre_token, post_token):
        self.pattern_token =


class PatternNameFeature(Feature):
    def __init__(self, pattern_token, pre_token, post_token):
        super(PatternNameFeature, self).__init__(pattern_token, pre_token, post_token)

    def token_to_value(self):
        return self.pattern_token.name


class PatternLengthFeature(Feature):
    def __init__(self, pattern_token, pre_token, post_token):
        super(PatternLengthFeature, self).__init__(pattern_token, pre_token, post_token)

    def token_to_value(self):
        if self.pattern_token.length != -1:
            return self.pattern_token.length
        return 0

class PatternValueFeatureGenerator
