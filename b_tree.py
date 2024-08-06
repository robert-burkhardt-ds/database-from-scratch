class BTree:
    num_kv_size = 64
    num_children_size = 64
    node_size = 4096
    key_size = 64
    value_size = 64
    node_index_size = 64
    child_index_size = 64
    degree = 3
    byteorder = "big"
    def __init__(self, db_file=None):
        self.db_file = db_file

    def __enter__(self):
        self.file = open(self.db_file if self.db_file is not None else 'btree.db', 'r+b' if self.db_file is not None else 'w+b', buffering=0)
        self.file.seek(0)
        self.header = self._parse_header(self.file.read(self.node_size) or b'\x00' * self.node_size)
        self.file.seek(0)
        self.file.write(self._serialize_header(self.header))
        self.file.seek(self.header.root_index * self.node_size)
        root_data = self.file.read(self.node_size) or b'\x00' * self.node_size
        self.current_node = self._parse_node(root_data)
        return self

    def __exit__(self, _, __, ___):
        self.file.seek(0)
        self.file.write(self._serialize_header(self.header))
        self.file.close()

    def _serialize_header(self, header):
        out = bytearray(self.node_size)
        out[:self.node_index_size] = header.root_index.to_bytes(self.node_index_size, byteorder=self.byteorder)
        base_offset = self.node_index_size
        for i, orphan in enumerate(header.orphans):
            curr_offset = base_offset + (i * self.child_index_size)
            out[curr_offset:curr_offset + self.child_index_size] = orphan.to_bytes(self.child_index_size, byteorder=self.byteorder)
        return bytes(out)

    def _parse_header(self, data):
        root_index = int.from_bytes(data[:self.node_index_size], byteorder=self.byteorder) or 1
        offset = self.node_index_size
        possible_orphan = data[offset:offset + self.child_index_size]
        orphans = []
        while possible_orphan != b'\x00' * self.child_index_size:
            orphan = int.from_bytes(possible_orphan, byteorder=self.byteorder)
            orphans.append(orphan)
            offset += self.child_index_size
            possible_orphan = data[offset:offset + self.child_index_size]
        return Header(root_index, orphans)
    
    def _serialize_node(self, node):
        out = bytearray(self.node_size)
        out[:self.num_kv_size] = len(node.key_values).to_bytes(self.num_kv_size, byteorder=self.byteorder)
        base_offset = self.num_kv_size
        for i in range(self.degree - 1):
            curr_offset = base_offset + (i * (self.key_size + self.value_size))
            if i < len(node.key_values):
                kv = node.key_values[i]
                out[curr_offset:curr_offset + self.key_size + self.value_size] = kv.key.to_bytes(self.key_size, byteorder=self.byteorder) + kv.value.to_bytes(self.value_size, byteorder=self.byteorder)
            else:
                out[curr_offset:curr_offset + self.key_size + self.value_size] = (b'\x00' * self.key_size) + (b'\x00' * self.value_size)
        child_base_offset = self.num_kv_size + (self.degree - 1) * (self.key_size + self.value_size)
        out[child_base_offset:child_base_offset + self.num_children_size] = len(node.children).to_bytes(self.num_children_size, byteorder=self.byteorder)
        child_offset_after_len = child_base_offset + self.num_children_size
        for i in range(self.degree):
            curr_offset = child_offset_after_len + (i * self.child_index_size)
            if i < len(node.children):
                child = node.children[i]
                out[curr_offset:curr_offset + self.child_index_size] = child.to_bytes(self.child_index_size, byteorder=self.byteorder)
            else:
                out[curr_offset:curr_offset + self.child_index_size] = b'\x00' * self.child_index_size
        return bytes(out)

    def _parse_node(self, data):
        num_key_values = int.from_bytes(data[:self.num_kv_size], byteorder=self.byteorder)
        raw_key_values = data[self.num_kv_size:self.num_kv_size + ((self.degree - 1) * (self.key_size + self.value_size))]
        key_values = []
        for i in range(num_key_values):
            offset = i * (self.key_size + self.value_size)
            kv = raw_key_values[offset:offset + (self.key_size + self.value_size)]
            raw_key = kv[:self.key_size]
            raw_value = kv[self.key_size:self.key_size + self.value_size]
            key = int.from_bytes(raw_key, byteorder=self.byteorder)
            value = int.from_bytes(raw_value, byteorder=self.byteorder)
            key_values.append(KeyValue(key, value))
        children_offset = self.num_kv_size + ((self.degree - 1) * (self.key_size + self.value_size))
        num_children = int.from_bytes(data[children_offset:children_offset + self.num_children_size], byteorder=self.byteorder)
        raw_children = data[children_offset + self.num_children_size:children_offset + self.num_children_size + (self.degree * self.child_index_size)]
        children = []
        for i in range(num_children):
            offset = i * (self.child_index_size)
            raw_child = raw_children[offset:offset + (self.child_index_size)]
            child = int.from_bytes(raw_child, byteorder=self.byteorder)
            children.append(child)
        return Node(key_values, children)
    
    def get(self, key):
        self.file.seek(self.header.root_index * self.node_size)
        root_data = self.file.read(self.node_size) or b'\x00' * self.node_size
        self.current_node = self._parse_node(root_data)
        kv, _ = self._get(key, self.header.root_index)
        return kv.value if kv is not None else None
    
    def _get(self, key, node_index):
        matched_kv = None
        candidate_nodes = []
        i = 0
        try_child = False
        while i < len(self.current_node.key_values) and matched_kv is None and not try_child:
            current_kv = self.current_node.key_values[i]
            current_key = current_kv.key
            if current_key == key:
                matched_kv = current_kv
            elif current_key < key:
                i += 1
            else:
                try_child = True
        if matched_kv is None and i < len(self.current_node.children):
            new_node_index = self.current_node.children[i]
            self.file.seek(new_node_index * self.node_size)
            new_node_data = self.file.read(self.node_size)
            self.current_node = self._parse_node(new_node_data)
            matched_kv, candidate_nodes = self._get(key, new_node_index)
        return matched_kv, [node_index, *candidate_nodes]
    
    def set(self, key, value):
        self.file.seek(self.header.root_index * self.node_size)
        root_data = self.file.read(self.node_size) or b'\x00' * self.node_size
        self.current_node = self._parse_node(root_data)
        prev_value = self._set(key, value)
        return prev_value

    def _set(self, key, value):
        kv, node_idxs = self._get(key, self.header.root_index)
        previous_value = None
        if kv is not None:
            previous_value = kv.value
            kv.value = value
            self.file.seek(self.header.root_index * self.node_size)
            self.file.write(self._serialize_node(self.current_node))
        else:
            node_index = node_idxs.pop()
            self.file.seek(node_index * self.node_size)
            node_data = self.file.read(self.node_size)
            self.current_node = self._parse_node(node_data)
            if len(self.current_node.key_values) < self.degree:
                i = 0
                found_insert_position = False
                while i < len(self.current_node.key_values) and not found_insert_position:
                    current_key = self.current_node.key_values[i].key
                    if current_key < key:
                        i += 1
                    else:
                        found_insert_position = True
                self.current_node.key_values.insert(i, KeyValue(key, value))
            curr_index = node_index
            balanced = False
            while not balanced:
                if len(self.current_node.key_values) < self.degree:
                    balanced = True
                    self.file.seek(curr_index * self.node_size)
                    self.file.write(self._serialize_node(self.current_node))
                else:
                    median_index = self.degree // 2
                    children_index = len(self.current_node.children) // 2
                    median = self.current_node.key_values[median_index]
                    median_key = median.key
                    self.file.seek(0, 2)
                    lesser_next_idx = self.file.tell() // self.node_size if len(self.header.orphans) == 0 else self.header.orphans.pop()
                    new_lesser_node = Node(key_values=self.current_node.key_values[:median_index], children=self.current_node.children[:children_index])
                    lesser_children = [lesser_next_idx]
                    self.file.seek(lesser_next_idx * self.node_size)
                    self.file.write(self._serialize_node(new_lesser_node))
                    new_greater_node = Node(key_values=self.current_node.key_values[median_index + 1:], children=self.current_node.children[children_index:])
                    self.file.seek(0, 2)
                    greater_next_idx = self.file.tell() // self.node_size if len(self.header.orphans) == 0 else self.header.orphans.pop()
                    greater_children = [greater_next_idx]
                    self.file.seek((greater_next_idx) * self.node_size)
                    self.file.write(self._serialize_node(new_greater_node))
                    self.file.seek(0, 2)
                    last_idx = self.file.tell() // self.node_size
                    candidate_parent_index = node_idxs.pop() if len(node_idxs) != 0 else last_idx if len(self.header.orphans) == 0 else self.header.pop()
                    self.file.seek(candidate_parent_index * self.node_size)
                    parent_data = self.file.read(self.node_size)
                    self.current_node = self._parse_node(parent_data)
                    parent_insertion_index = 0
                    found_parent_position = False
                    while parent_insertion_index < len(self.current_node.key_values) and not found_parent_position:
                        if median_key > self.current_node.key_values[parent_insertion_index].key:
                            parent_insertion_index += 1
                        else:
                            found_parent_position = True
                    self.current_node.key_values.insert(parent_insertion_index, median)
                    self.current_node.children = self.current_node.children[:parent_insertion_index] + lesser_children + greater_children + self.current_node.children[parent_insertion_index + 1:]
                    self.header.orphans.append(curr_index)
                    self.file.seek(0)
                    self.file.write(self._serialize_header(self.header))
                    curr_index = candidate_parent_index
            if len(node_idxs) == 0:
                self.header.root_index = curr_index
                self.file.seek(0)
                self.file.write(self._serialize_header(self.header))
        return previous_value

class Header:
    def __init__(self, root_index, orphans):
        self.root_index = root_index
        self.orphans = orphans

class Node:
    def __init__(self, key_values=None, children=None):
        self.key_values = key_values if key_values is not None else []
        self.children = children if children is not None else []

class KeyValue:
    def __init__(self, key, value):
        self.key = key
        self.value = value