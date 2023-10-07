import asyncio
import os
import tempfile

from app.server import AsyncServer


async def main():
    print("Start program")

    # Получаем переменные окружения; используем значения по умолчанию, если они не заданы
    start_id = int(os.environ.get('START_ID', 19748419))
    end_id = int(os.environ.get('END_ID', 39749429))
    batch_size = int(os.environ.get('BATCH_SIZE', 100000))

    server = AsyncServer(debug=True)  # Используйте ваши параметры здесь

    for i in range(start_id, end_id, batch_size):
        camera_ids = [str(j) for j in range(i, min(i + batch_size, end_id + 1))]
        await server.check_camera_batch(camera_ids)


if __name__ == "__main__":
    asyncio.run(main())
