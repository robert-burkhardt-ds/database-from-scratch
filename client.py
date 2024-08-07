import asyncio
import random
import time
import statistics
from multiprocessing import Process

times = []

async def send_data():
    keys = list(range(int(1e6)))
    random.shuffle(keys)
    trial_keys = keys[:int(1e5)]
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for key in trial_keys:
        start_time = time.perf_counter_ns()
        writer.write(b'\x00\x02' + (key).to_bytes(64, byteorder="big") + b'\x00' * 191)
        data = b''
        while len(data) != 256:
            recvd = await reader.read(256)
            data += recvd
        end_time = time.perf_counter_ns()
        assert int.from_bytes(data[1:65], byteorder="big") // 10 == key
        times.append(end_time - start_time)
    print(f'Avg read time (ns): {statistics.mean(times)}')
    writer.close()
    await writer.wait_closed()

def run_client():
    asyncio.run(send_data())

if __name__ == '__main__':
    ps = []

    for i in range(100):
        p = Process(target=run_client)
        p.start()

    for p in ps:
        p.join()