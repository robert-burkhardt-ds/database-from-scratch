from b_tree import BTree, Node, KeyValue

tree = BTree()

tree.set(1, 'foo')
tree.set(2, 'bar')
tree.set(3, 'baz')
tree.set(4, 'baz')
tree.set(1.5, 'safdsa')
print(tree.get(1))
print(tree.get(2))
print(tree.get(3))
print(tree.get(4))
print(tree.set(4, 'qux'))
print(tree.get(4))
print(tree.get(1.5))


# tree.root.key_values = []
# print(tree.get(1))

# tree.root.key_values = [KeyValue(1, "foo")]
# print(tree.get(1))
# print(tree.get(2))

# tree.root.key_values = [KeyValue(1, "foo"), KeyValue(2, "bar")]
# print(tree.get(1))
# print(tree.get(2))
# print(tree.get(3))

# tree.root.key_values = [KeyValue(2, "bar")]
# tree.root.children = [Node(key_values=[KeyValue(1, "foo")]), Node(key_values=[KeyValue(3, "baz")])]
# print(tree.get(1))
# print(tree.get(2))
# print(tree.get(3))
# print(tree.get(4))

# tree.root.key_values = [KeyValue(2, "bar")]
# tree.root.children = [Node(key_values=[KeyValue(1, "foo")]), Node(key_values=[KeyValue(3, "baz"), KeyValue(4, "qux")])]
# print(tree.get(1))
# print(tree.get(2))
# print(tree.get(3))
# print(tree.get(4))
# print(tree.get(5))

# tree.root.key_values = [KeyValue(2, "bar")]
# tree.root.children = [Node(key_values=[KeyValue(1, "foo")]), Node(key_values=[KeyValue(3, "baz"), KeyValue(4, "qux")])]
# print(tree._get(1, tree.root))
