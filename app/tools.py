import struct


class ToolsClass:
    @staticmethod
    def parse_relay_server(data):
        """
        Parse the relay server data.

        Parameters:
            data (bytes): The data to be parsed.

        Returns:
            dict or None: A dictionary containing the parsed data or None if parsing fails.
        """
        try:
            # Ensure the data is in the expected format
            if data[1:3] != b'\x00\x00':
                # Extract relevant information from the data
                device_id = data[1:9].decode('utf-8')
                relay_server = data[33:data.find(b'\x00', 33)].decode('utf-8')
                relay_port = struct.unpack('<H', data[50:52])[0]

                # Log the extracted information
                print(f'\u001b[32m[+] Relay found for id {device_id} {relay_server}:{relay_port}\u001b[37m')

                # Return the extracted information as a dictionary
                return {
                    'id': device_id,
                    'relay_server': relay_server,
                    'relay_port': relay_port
                }
            else:
                return None
        except Exception as e:
            # Log any exceptions that occur during parsing
            print(f"An error occurred while parsing the relay server data: {str(e)}")
            return None
