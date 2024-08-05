from b_tree import BTree

with BTree() as tree:
    tree.set(1, 10)
    tree.set(2, 20)
    tree.set(3, 30)
    tree.set(4, 40)

    print(tree.get(1))
    print(tree.get(2))
    print(tree.get(3))
    print(tree.get(4))
    print(tree.set(4, 45))
    print(tree.get(4))
    print(tree.get(5))

with BTree('wal.bin') as tree:
    print(tree.get(1))
    print(tree.get(2))
    print(tree.get(3))
    print(tree.get(4))
    print(tree.get(5))