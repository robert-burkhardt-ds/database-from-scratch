import time
import random
import statistics
from b_tree import BTree

random.seed(42)

write_times = []
read_times = []

with BTree() as db:
    keys = list(range(int(1e6)))
    for key in keys:
        start = time.process_time_ns()
        db.set(key, key * 10)
        end = time.process_time_ns()
        write_times.append(end - start)
    shuffled_keys = list(keys)
    random.shuffle(shuffled_keys)
    for key in shuffled_keys:
        start = time.process_time_ns()
        val = db.get(key)
        assert key == val / 10
        end = time.process_time_ns()
        read_times.append(end - start)

first_start = time.process_time_ns()
with BTree('wal.bin') as db:
    pass
first_end = time.process_time_ns()

second_start = time.process_time_ns()
with BTree('wal.bin') as db:
    pass
second_end = time.process_time_ns()

print(f'Write avg: {statistics.mean(write_times)}')
print(f'Write std dev: {statistics.stdev(write_times)}')

print(f'Read avg: {statistics.mean(read_times)}')
print(f'Read std dev: {statistics.stdev(read_times)}')

print(f'Time to first load: {first_end - first_start}')
print(f'Time to second load: {second_end - second_start}')