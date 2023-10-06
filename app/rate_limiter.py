import asyncio
import time


class RateLimiter:
    def __init__(self, max_requests, period):
        self.max_requests = max_requests  # Максимальное количество запросов за период
        self.period = period  # Период времени в секундах
        self.allowance = max_requests  # Начальное количество разрешенных запросов
        self.last_check = time.time()  # Время последней проверки ограничителя скорости

    async def request_allowed(self):
        current_time = time.time()
        time_passed = current_time - self.last_check
        self.last_check = current_time
        self.allowance += time_passed * (self.max_requests / self.period)

        if self.allowance > self.max_requests:
            self.allowance = self.max_requests  # Ограничиваем

        if self.allowance < 1.0:
            # Недостаточно квоты для выполнения запроса
            return False
        else:
            # Разрешаем запрос
            self.allowance -= 1.0
            return True

    async def wait_for_request_slot(self):
        while not await self.request_allowed():
            await asyncio.sleep(0.1)  # Спим немного перед следующей проверкой
