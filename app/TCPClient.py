import asyncio


class TCPClient:
    def __init__(self, server, port):
        self.server = server
        self.port = port

    async def send_data(self, data, timeout):
        if not isinstance(self.server, str):
            raise TypeError("Server must be a string")
        writer = None
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.server, self.port),
                timeout=timeout
            )
            writer.write(data)
            await writer.drain()
            response = await reader.read(4096)
            return response
        except (ConnectionRefusedError, IndexError, asyncio.TimeoutError, asyncio.CancelledError):
            return None
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()
