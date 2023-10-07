import asyncio
import tempfile

from app.server import AsyncServer


async def main():
    start_id = 19748419
    end_id = 19748420
    batch_size = 1000  # Размер пачки ID для одновременной проверки

    server = AsyncServer(debug=True)  # Используйте ваши параметры здесь

    async for camera_ids in server.camera_id_generator(start_id, end_id, batch_size):
        # Проверка пачки ID камер
        await server.check_camera_batch(camera_ids)


if __name__ == "__main__":
    asyncio.run(main())
