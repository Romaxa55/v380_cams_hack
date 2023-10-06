import asyncio
import tempfile

from app.server import AsyncServer


async def main():
    start_id = 19451485
    end_id = 19551490
    batch_size = 1000  # Размер пачки ID для одновременной проверки

    server = AsyncServer()  # Используйте ваши параметры здесь

    # Создание временного файла для хранения результатов
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        async for camera_ids in server.camera_id_generator(start_id, end_id, batch_size):
            # Проверка пачки ID камер
            results = await server.check_camera_batch(camera_ids)

            # Запись результатов во временный файл
            for camera_id, is_online in zip(camera_ids, results):
                temp_file.write(f"{camera_id},{is_online}\n")

        print(f"Results written to {temp_file.name}")

if __name__ == "__main__":
    asyncio.run(main())
