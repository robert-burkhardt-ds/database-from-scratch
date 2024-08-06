from b_tree import BTree
import random

random.seed(42)

with BTree() as db:
    keys = list(range(int(1e6)))
    random.shuffle(keys)
    for key in keys:
        db.set(key, key * 10)