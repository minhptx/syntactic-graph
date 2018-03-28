from collections import defaultdict


class Cache:
    def __init__(self):
        self.ev_hash = defaultdict(lambda: [])
