class BTree:
    key_size = 64
    value_size = 64
    degree = 3
    byteorder = "big"
    def __init__(self, wal_name=None):
        self.root = Node()
        self.wal_name = wal_name

    def __enter__(self):
        self.file = open(self.wal_name, '+ab', buffering=0) if self.wal_name is not None else open('wal.bin', '+wb', buffering=0)
        self.file.seek(0)
        byte_key, byte_value = self.file.read(self.key_size), self.file.read(self.value_size)
        while byte_key and byte_value:
            key = int.from_bytes(byte_key, byteorder=self.byteorder)
            value = int.from_bytes(byte_value, byteorder=self.byteorder)
            self._set(key, value)
            byte_key, byte_value = self.file.read(self.key_size), self.file.read(self.value_size)
        return self

    def __exit__(self, _, __, ___):
        self.file.close()
    
    def get(self, key):
        kv, _ = self._get(key, self.root)
        return int.from_bytes(kv.value, byteorder=self.byteorder) if kv is not None else None
    
    def _get(self, key, node):
        matched_kv = None
        candidate_nodes = []
        i = 0
        try_child = False
        while i < len(node.key_values) and matched_kv is None and not try_child:
            current_kv = node.key_values[i]
            current_key = int.from_bytes(current_kv.key, byteorder=self.byteorder)
            if current_key == key:
                matched_kv = current_kv
            elif current_key < key:
                i += 1
            else:
                try_child = True
        if matched_kv is None and i < len(node.children):
            matched_kv, candidate_nodes = self._get(key, node.children[i])
        return matched_kv, [node, *candidate_nodes]
    
    def set(self, key, value):
        byte_key = key.to_bytes(self.key_size, byteorder=self.byteorder)
        byte_value = value.to_bytes(self.value_size, byteorder=self.byteorder)
        self.file.write(byte_key + byte_value)
        prev_value = self._set(key, value)
        return prev_value

    def _set(self, key, value):
        byte_key = key.to_bytes(self.key_size, byteorder=self.byteorder)
        byte_value = value.to_bytes(self.value_size, byteorder=self.byteorder)
        kv, nodes = self._get(key, self.root)
        previous_value = None
        if kv is not None:
            previous_value = kv.value
            kv.value = byte_value
        else:
            node = nodes.pop()
            if len(node.key_values) < self.degree:
                i = 0
                while i < len(node.key_values):
                    current_key = int.from_bytes(node.key_values[i].key, byteorder=self.byteorder)
                    if current_key < key:
                        i += 1
                node.key_values.insert(i, KeyValue(byte_key, byte_value))
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
        return int.from_bytes(previous_value, byteorder=self.byteorder) if previous_value is not None else None


class Node:
    def __init__(self, key_values=None, children=None):
        self.key_values = key_values if key_values is not None else []
        self.children = children if children is not None else []

class KeyValue:
    def __init__(self, key, value):
        self.key = key
        self.value = value