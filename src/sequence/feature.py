def token_to_features(edge):
    feature_dict = {}
    for ev in edge.value_list:
        feature_dict["Name=%s" % ev.atomic.name] = 1
        # feature_dict["PreName"] = pre_token.name
        # feature_dict["PostName"] = post_token.name

        feature_dict["Length=%s" % ev.length] = 1

        for text in ev.values:
            feature_dict["Word=%s" % text] = 1
        return feature_dict
