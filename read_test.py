import random
import time
import matplotlib.pyplot as plt
from b_tree import BTree

random.seed(839)

all_keys = list(range(int(1e6)))
random.shuffle(all_keys)
test_keys = all_keys[:10]

all_time_diffs = []

for f in range(1, 4):
    time_diffs = []
    with BTree(f'test{f}.db') as db:
        for key in test_keys:
            start_time = time.perf_counter_ns()
            val = db.get(key)
            end_time = time.perf_counter_ns()
            assert val // 10 == key
            time_diffs.append(end_time - start_time)
    all_time_diffs.append(time_diffs)

avg_time_diffs = []

for i in range(len(all_time_diffs[0])):
    sum = 0
    for j in range(len(all_time_diffs)):
        sum += all_time_diffs[j][i]
    avg_time_diffs.append(sum / len(all_time_diffs))

plt.plot(list(range(len(all_time_diffs[0]))), avg_time_diffs)
plt.xlabel('Read iteration')
plt.ylabel('Time (ns)')
plt.title('Node/Page read speed over time')
plt.show()
