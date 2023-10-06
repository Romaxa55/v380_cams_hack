import asyncio
import random
from app.rate_limiter import RateLimiter


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
                 max_requests_per_minute=300):
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

    async def check_camera(self, camera_id, max_retries=5):
        """
        Asynchronously check a single camera with exponential backoff retry strategy.

        Parameters:
        - camera_id (str): The ID of the camera to check.
        - max_retries (int): The maximum number of retries.

        Returns:
        - bool: True if the camera is online, False otherwise.
        """
        for retry in range(max_retries):
            await self.rate_limiter.wait_for_request_slot()
            response = await self.send_request(camera_id)

            if response is not None:
                if response[4] == 1:
                    print(f'\u001b[32m[+] Camera with ID: {camera_id} is online!\u001b[37m')
                    return True
                else:
                    return False

            wait_time = (2 ** retry) + random.uniform(0, 0.2 * (2 ** retry))
            print(f'\u001b[32m[+] Error: Connection failed... retrying in {wait_time:.2f} seconds...\u001b[37m')
            await asyncio.sleep(wait_time)

        print(
            f'\u001b[31m[-] Camera with ID: {camera_id} is offline or not responding after {max_retries} retries!\u001b[37m')
        return False

    async def single_request_check(self):
        """
        Asynchronously check the server with a single request.

        Returns:
        - bool: True if the server responds positively, False otherwise.
        """
        response = await self.send_request("10000000")

        return response is not None and response[4] == 1

    async def send_request(self, camera_id, timeout=5.0):
        """
        Send a request to the server and return the response.

        Parameters:
        - camera_id (str): The ID of the camera to check.
        - timeout (float): The timeout for the connection attempt.

        Returns:
        - bytes: The response from the server, or None if the request failed.
        """
        hexID = bytes(str(camera_id), 'utf-8').hex()
        data = (
                'ac000000f3030000' +
                hexID +
                '2e6e766476722e6e657400000000000000000000000000006022000093f5d10000000000000000000000000000000000'
        )
        data = bytes.fromhex(data)
        writer = None

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.server_checker, self.port_checker),
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

    async def checker_online(self, list_ids):
        """
        Asynchronously check multiple cameras.
        """
        tasks = []
        for i in list_ids:
            if i:
                tasks.append(self.check_camera(i))
        await asyncio.gather(*tasks)

    async def create_socket(self, dev):
        """
        Asynchronously create a socket and check a camera.
        """
        # Implement the logic for creating a socket and checking a camera asynchronously
        pass

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
