def lcs(a, b):
    lengths = [[0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x - 1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y - 1]:
            y -= 1
        else:
            assert a[x - 1] == b[y - 1]
            result = a[x - 1] + result
            x -= 1
            y -= 1
    return result


def jaccard_similarity(set_1, set_2):
    set_1 = set(set_1)
    set_2 = set(set_2)

    n = len(set_1.intersection(set_2))
    # print(set_1, set_2, n)
    try:
        return n / float(len(set_1) + len(set_2) - n)
    except Exception as e:
        print(e)
        return 0


def jaccard_subset_similarity(set_1, set_2):
    n = 0
    count = 0
    for value_1 in set_1:
        for value_2 in set_2:
            if value_1 in value_2:
                n += len(value_1) * 1.0 / len(value_2)
                count += 1
                break

    return n / float(len(set_1) + len(set_2) - count)
