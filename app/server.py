import asyncio
import random
import socket

from app.rate_limiter import RateLimiter
from app.TCPClient import TCPClient
from app.UDPClient import UDPClient
from app.tools import ToolsClass
from app.handler import DataHandler


class AsyncServer:
    """
    AsyncServer Class

    This class is designed to manage and check cameras asynchronously.
    It provides methods to check the status of a single camera or multiple cameras in parallel.

    Attributes:
    - server (str): The server address to check the camera(s).
    - port (int): The port number to use for checking.
    - timeout (int): The timeout value for checking a camera.
    - file_list_cams (str): The file name where the list of cameras is stored.
    - pass_file (str): The file name where the password is stored.
    - debug (bool): A flag to enable/disable debug mode.

    Methods:
    - async check_camera(dev): Asynchronously check a single camera.
    - async checker_online(list_ids): Asynchronously check multiple cameras.
    - async create_socket(dev): Asynchronously create a socket and check a camera.
    """

    def __init__(self, server='ipc1300.av380.net', port=8877, timeout=300,
                 file_list_cams='cams.txt', pass_file='pass.txt', debug=False,
                 server_checker='149.129.177.248', port_checker=8900,
                 max_requests_per_minute=300, relay_queue=None):
        """
        Initializes the AsyncServer with the provided parameters.

        Parameters:
        - server (str): The server address. Default is 'ipc1300.av380.net'.
        - port (int): The port number. Default is 8877.
        - timeout (int): The timeout value. Default is 300.
        - file_list_cams (str): The file name for camera list. Default is 'cams.txt'.
        - pass_file (str): The file name for password. Default is 'pass.txt'.
        - debug (bool): Enable/disable debug mode. Default is False.
        - server_checker (str): The server address for checking cameras. Default is '149.129.177.248'.
        - port_checker (int): The port number for checking cameras. Default is 8900.
        """
        self.rate_limiter = RateLimiter(max_requests=max_requests_per_minute, period=60)
        self.server = server
        self.port = port
        self.timeout = timeout
        self.file_list_cams = file_list_cams
        self.pass_file = pass_file
        self.debug = debug
        self.server_checker = server_checker
        self.port_checker = port_checker
        self.tools = ToolsClass()

    async def check_camera(self, camera_id, max_retries=5):
        """
        Asynchronously check a single camera with exponential backoff retry strategy.

        Parameters:
        - camera_id (str): The ID of the camera to check.
        - max_retries (int): The maximum number of retries.

        Returns:
        - bool: True if the camera is online, False otherwise.
        """
        hexID = bytes(str(camera_id), 'utf-8').hex()
        data = (
                'ac000000f3030000' +
                hexID +
                '2e6e766476722e6e657400000000000000000000000000006022000093f5d10000000000000000000000000000000000'
        )
        data = bytes.fromhex(data)

        for retry in range(max_retries):
            await self.rate_limiter.wait_for_request_slot()
            response = await self.send_request(self.server_checker, self.port_checker, data,
                                               socket_type=socket.SOCK_STREAM)

            if response is not None:
                if response[4] == 1:
                    print(f'\u001b[32m[+] Camera with ID: {camera_id} is online!\u001b[37m')
                    relay = await self.create_socket(camera_id)
                    if relay:
                        await self.connect_to_relay(relay, camera_id)
                    return True
                else:
                    return False

            wait_time = (2 ** retry) + random.uniform(0, 0.2 * (2 ** retry))
            print(f'\u001b[32m[+] Error: Connection failed... retrying in {wait_time:.2f} seconds...\u001b[37m')
            await asyncio.sleep(wait_time)

        print(
            f'\u001b[31m[-] Camera with ID: {camera_id} is offline or not responding after {max_retries} retries!\u001b[37m')
        return False

    async def connect_to_relay(self, relay_data, camera_id):
        # Проверка, что relay_data не является None и содержит необходимые данные
        if relay_data and 'id' in relay_data and 'relay_server' in relay_data and 'relay_port' in relay_data:
            data = '32'
            data += bytes(str(relay_data['id']), 'utf-8').hex()
            data += '2e6e766476722e6e65740000000000000000000000000000302e30' \
                    '2e302e30000000000000000000018a1bc4d62f4a41ae000000000000 '
            data = bytes.fromhex(data)

            local_relay_queue = asyncio.Queue()

            data_handler_instance = DataHandler(camera_id=camera_id, relay_queue=local_relay_queue)

            # Отправка данных на релейный сервер
            return await self.send_request(relay_data['relay_server'],
                                           relay_data['relay_port'],
                                           data,
                                           socket_type=socket.SOCK_DGRAM,
                                           timeout=30,
                                           data_handler=data_handler_instance.handle_data
                                           )
        else:
            print("\u001b[31m[-] Parsing relay data failed or received unexpected structure\u001b[37m")
            return None

    async def create_socket(self, camera_id):
        try:

            if self.debug:
                print(f"\u001b[32m[+] Send request for id: {camera_id}\u001b[37m")

            data = '02070032303038333131323334333734313100020c17222d0000'
            data += bytes(str(camera_id), 'utf-8').hex()
            data += '2e6e766476722e6e65740000000000000000000000000000'
            data += '3131313131313131313131318a1bc0a801096762230a93f5d100'
            data = bytes.fromhex(data)

            local_relay_queue = asyncio.Queue()

            data_handler_instance = DataHandler(camera_id=camera_id, relay_queue=local_relay_queue)

            # Отправка данных через UDP
            await self.send_request(self.server,
                                    self.port, data,
                                    socket_type=socket.SOCK_DGRAM,
                                    timeout=30,
                                    data_handler=data_handler_instance.handle_data
                                    )

            try:
                # Блокировка выполнения до тех пор, пока в очереди не появится элемент
                return await asyncio.wait_for(local_relay_queue.get(), timeout=3)
            except asyncio.TimeoutError:
                return None
            except Exception as e:
                print(f"[ERROR] An error occurred while waiting for relay data: {str(e)}")
                return None
            else:
                print("[INFO] Relay data received:", result)
                return None

        except asyncio.TimeoutError:
            print(f"\u001b[33m[-] Timeout while waiting for response for camera id: {camera_id}\u001b[37m")
            return None

    @staticmethod
    async def send_request(server, port, data, socket_type=socket.SOCK_STREAM, timeout=30, data_handler=None):
        """
        Send a request to the server and return the response.

        Parameters:
        - server (str): The server IP or hostname to send data to.
        - port (int): The server port to send data to.
        - data (bytes): The data to send to the server.
        - socket_type (int, optional): The type of the socket (SOCK_STREAM or SOCK_DGRAM). Defaults to SOCK_STREAM.
        - timeout (float, optional): The timeout for the connection attempt. Defaults to 30.
        - data_handler (callable, optional): A function to handle received UDP data.
                                             Must be `async def` if it performs asynchronous operations.
                                             Only applicable if socket_type is SOCK_DGRAM. Defaults to None.

        Returns:
        - bytes: The response from the server, or None if the request failed.
        """
        if socket_type == socket.SOCK_STREAM:
            client = TCPClient(server, port)
            return await client.send_data(data, timeout)
        elif socket_type == socket.SOCK_DGRAM:
            client = UDPClient(server, port)
            return await client.send_data(data, data_handler)
        else:
            raise ValueError("Invalid socket type")

    async def checker_online(self, list_ids):
        """
        Asynchronously check multiple cameras.
        """
        tasks = []
        for i in list_ids:
            if i:
                tasks.append(self.check_camera(i))
        await asyncio.gather(*tasks)



    async def check_camera_batch(self, camera_ids):
        """
        Asynchronously check a batch of cameras.
        """
        tasks = [self.check_camera(camera_id) for camera_id in camera_ids]
        return await asyncio.gather(*tasks)

    @staticmethod
    async def camera_id_generator(start_id, end_id, batch_size):
        """
        Asynchronous generator to yield batches of camera IDs.
        """
        for i in range(start_id, end_id, batch_size):
            yield [str(j) for j in range(i, min(i + batch_size, end_id + 1))]
