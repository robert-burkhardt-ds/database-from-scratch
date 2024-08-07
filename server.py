from b_tree import BTree
import asyncio

with BTree('server.db') as db:
    async def handle_request(reader, writer):
        should_continue = True
        while should_continue:
            data = await reader.read(256)
            if data:
                command = data[:2]
                if command == b'\x00\x01':
                    # print('Recieved contains query')
                    key = data[2:64 + 2]
                    val = 1 if db.get(int.from_bytes(key, byteorder="big")) is not None else 0
                    writer.write(val.to_bytes(1, byteorder="big"))
                    writer.write(b'\x00' * 255)
                if command == b'\x00\x02':
                    # print('Received get query')
                    key = data[2:64 + 2]
                    val = db.get(int.from_bytes(key, byteorder="big"))
                    signal = 1 if val is not None else 0
                    writer.write(signal.to_bytes(1, byteorder="big"))
                    writer.write(val.to_bytes(64, byteorder="big"))
                    writer.write(b'\x00' * 191)
                if command == b'\x00\x03':
                    # print('Received set query')
                    key = data[2:64 + 2]
                    value = data[68:132]
                    existing_val = db.set(int.from_bytes(key, byteorder="big"), int.from_bytes(value, byteorder="big"))
                    signal = 1 if existing_val is not None else 0
                    writer.write(signal.to_bytes(1, byteorder="big"))
                    writer.write(existing_val.to_bytes(64, byteorder="big"))
                    writer.write(b'\x00' * 191)
                await writer.drain()
            else:
                print("Close the connection")
                writer.close()
                await writer.wait_closed()
                should_continue = False

    async def main():
        server = await asyncio.start_server(handle_request, '127.0.0.1', 8888)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')
        async with server:
            await server.serve_forever()

    asyncio.run(main())
