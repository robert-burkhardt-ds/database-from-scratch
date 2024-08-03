class BTree:
    def __init__(self, degree=3):
        self.root = Node()
        self.degree = degree
    
    def get(self, key):
        kv, _ = self._get(key, self.root)
        return kv.value if kv is not None else None
    
    def _get(self, key, node):
        matched_kv = None
        candidate_nodes = []
        i = 0
        try_child = False
        while i < len(node.key_values) and matched_kv is None and not try_child:
            current_kv = node.key_values[i]
            if current_kv.key == key:
                matched_kv = current_kv
            elif node.key_values[i].key < key:
                i += 1
            else:
                try_child = True
        if matched_kv is None and i < len(node.children):
            matched_kv, candidate_nodes = self._get(key, node.children[i])
        return matched_kv, [node, *candidate_nodes]

    def set(self, key, value):
        previous_value = None
        kv, nodes = self._get(key, self.root)
        if kv is not None:
            previous_value = kv.value
            kv.value = value
        else:
            node = nodes.pop()
            if len(node.key_values) < self.degree:
                i = 0
                while i < len(node.key_values):
                    if node.key_values[i].key < key:
                        i += 1
                node.key_values.insert(i, KeyValue(key, value))
            if len(node.key_values) == self.degree:
                median_index = self.degree // 2
                median = node.key_values[median_index]
                lesser_children = [Node(key_values=node.key_values[0:median_index])]
                greater_children = [Node(key_values=node.key_values[median_index + 1:])]
                candidate_parent = nodes.pop() if len(nodes) != 0 else Node()
                balanced = False
                while not balanced:
                    candidate_parent.key_values.append(median)
                    candidate_parent.children.extend(lesser_children)
                    candidate_parent.children.extend(greater_children)
                    if len(candidate_parent.key_values) == self.degree:
                        median_index = self.degree // 2
                        median = candidate_parent.key_values[median_index]
                        lesser_children = candidate_parent.children[0:median_index]
                        greater_children = candidate_parent.children[median_index + 1:]
                        candidate_parent = nodes.pop() if len(nodes) != 0 else Node()
                    else:
                        balanced = True
                if len(nodes) == 0:
                    self.root = candidate_parent
        return previous_value


class Node:
    def __init__(self, key_values=None, children=None):
        self.key_values = key_values if key_values is not None else []
        self.children = children if children is not None else []

class KeyValue:
    def __init__(self, key, value):
        self.key = key
        self.value = value