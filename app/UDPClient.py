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
        try:
            if not self.on_con_lost.done():
                self.on_con_lost.set_result(True)
        except asyncio.exceptions.InvalidStateError:
            pass


class UDPClient:
    def __init__(self, server, port):
        self.server = server
        self.port = port

    async def send_data(self, data, data_handler=None, timeout=30):
        """
        Отправка данных по UDP.

        :param data: байтовые данные для отправки.
        :param data_handler: опциональный асинхронный обработчик данных, вызываемый при получении данных.
        :param timeout: опциональный тайм-аут для запроса (по умолчанию 30 секунд).
        """
        loop = asyncio.get_running_loop()
        on_con_lost = loop.create_future()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientProtocol(on_con_lost, data_handler, loop),
            remote_addr=(self.server, self.port)
        )

        try:
            transport.sendto(data)
            await asyncio.wait_for(on_con_lost, timeout)  # управление тайм-аутом
        except asyncio.TimeoutError:
            pass
            # print(f"\u001b[33m[-] Timeout {self.server}:{self.port}\u001b[37m")
        finally:
            transport.close()
