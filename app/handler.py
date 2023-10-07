from app.tools import ToolsClass


class DataHandler:
    def __init__(self, camera_id):
        self.camera_id = camera_id

    async def handle_data(self, data, protocol):
        print(f"[INFO] Data received: {data} for camera_id: {self.camera_id}")
        if data and data[6:7] != b'\x00':
            parsed_data = ToolsClass.parse_relay_server(data)
            if parsed_data:
                print(parsed_data)
                protocol.active = False
                protocol.transport.close()

