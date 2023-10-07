import asyncio


class UDPClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, on_con_lost, data_handler, loop):
        self.loop = loop
        self.on_con_lost = on_con_lost
        self.data_handler = data_handler
        self.active = True
        self.transport = None

    def datagram_received(self, data, addr):
        # print(f"[INFO] Received response from {addr}: {data}")
        if self.active and self.data_handler is not None:
            asyncio.create_task(self.data_handler(data, self))

    def connection_made(self, transport):
        self.transport = transport

    def error_received(self, exc):
        print(f"[ERROR] Error received: {exc}")

    def connection_lost(self, exc):
        print("[ERROR] Connection lost")
        self.on_con_lost.set_result(True)


class UDPClient:
    def __init__(self, server, port):
        self.server = server
        self.port = port

    async def send_data(self, data, data_handler=None):
        loop = asyncio.get_running_loop()
        on_con_lost = loop.create_future()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientProtocol(on_con_lost, data_handler, loop),
            remote_addr=(self.server, self.port)
        )

        try:
            transport.sendto(data)
            await on_con_lost  # Ждем, пока соединение завершится
        except asyncio.TimeoutError:
            print("[ERROR] Timeout!")
        finally:
            transport.close()
