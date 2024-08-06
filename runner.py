from b_tree import BTree
import random


with BTree() as tree:
    keys = list(range(1, 10000))
    random.shuffle(keys)
    for key in keys:
        tree.set(key, key * 10)
    for key in keys:
        val = tree.get(key)
        assert val // 10 == key

# with BTree() as tree:
#     tree.set(8, 80)
#     tree.set(7, 70)
#     tree.set(6, 60)
#     tree.set(5, 50)
#     tree.set(4, 40)
#     tree.set(3, 30)
#     tree.set(2, 20)
#     tree.set(1, 10)
#     print(tree.get(8))
#     print(tree.get(7))
#     print(tree.get(6))
#     print(tree.get(5))
#     print(tree.get(4))
#     print(tree.get(3))
#     print(tree.get(2))
#     print(tree.get(1))

# with BTree() as tree:
#     tree.set(1, 10)
#     tree.set(2, 20)
#     tree.set(3, 30)
#     tree.set(4, 40)
#     tree.set(5, 50)
#     tree.set(6, 60)
#     tree.set(7, 70)
#     tree.set(8, 80)
#     print(tree.get(1))
#     print(tree.get(2))
#     print(tree.get(3))
#     print(tree.get(4))
#     print(tree.get(5))
#     print(tree.get(6))
#     print(tree.get(7))
#     print(tree.get(8))

# with BTree() as tree:
#     tree.set(4, 40)
#     tree.set(2, 20)
#     tree.set(3, 30)
#     tree.set(1, 10)

#     print(tree.get(1))
#     print(tree.get(2))
#     print(tree.get(3))
#     print(tree.get(4))
#     print(tree.set(4, 45))
#     print(tree.get(4))
#     print(tree.get(5))

# with BTree('wal.bin') as tree:
#     print(tree.get(1))
#     print(tree.get(2))
#     print(tree.get(3))
#     print(tree.get(4))
#     print(tree.get(5))