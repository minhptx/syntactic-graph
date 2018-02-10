def token_to_features(pattern_token, pre_token, post_token):
    feature_dict = []
    feature_dict["Name"] = pattern_token.name
    # feature_dict["PreName"] = pre_token.name
    # feature_dict["PostName"] = post_token.name

    feature_dict["Length"] = pattern_token.length

    for text in pattern_token.values:
        feature_dict["Word=%s" % text] = True
    print(feature_dict)
    return feature_dict