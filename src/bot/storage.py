from json import dump, load
from logging import getLogger

from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage, MemoryStorageRecord


logger = getLogger(__name__)


class MyMemoryStorage(MemoryStorage):
    def __init__(self):
        super().__init__()
        self.load_storage()

    def load_storage(self):
        try:
            with open("storage.json", "r", encoding="utf-8") as storage_file:
                json_data = load(storage_file)
        except FileNotFoundError:
            logger.info("Previous storage file not found.")
        else:
            for record in json_data:
                self.storage[StorageKey(**record["storage_key"])] = (
                    MemoryStorageRecord(**record["memory_storage_record"])
                )

    async def save_storage(self):
        serialized_data = []
        records = self.storage.items()

        for record in records:
            # Item has view like (StorageKey(...), MemoryStorageRecord(...))
            serialized_data.append(
                {
                    "storage_key": record[0].__dict__,
                    "memory_storage_record": record[1].__dict__,
                }
            )

        with open("storage.json", "w", encoding="utf-8") as storage_file:
            dump(serialized_data, storage_file, indent=2, ensure_ascii=False)


storage = MyMemoryStorage()
