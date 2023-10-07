import asyncio
import os
import tempfile

from app.server import AsyncServer


async def main():
    # Получаем переменные окружения; используем значения по умолчанию, если они не заданы
    start_id = int(os.environ.get('START_ID', 19348439))
    end_id = int(os.environ.get('END_ID', 19748452))
    batch_size = int(os.environ.get('BATCH_SIZE', 100))

    server = AsyncServer(debug=True)  # Используйте ваши параметры здесь

    async for camera_ids in server.camera_id_generator(start_id, end_id, batch_size):
        # Проверка пачки ID камер
        await server.check_camera_batch(camera_ids)


if __name__ == "__main__":
    asyncio.run(main())
