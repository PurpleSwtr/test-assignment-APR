import csv
from typing import Iterator


def get_csv_data(filename: str) -> Iterator[dict[str, str]]:
    """Читает данные из csv-файла и возвращает их в виде словарей.
    Файл должен быть в кодировке UTF-8.

    Args:
        filename (str): путь к csv-файлу.

    Yields:
        dict[str, str]:
            ключи - названия колонок,
            значения - данные текущей строки.

    Raises:
        FileNotFoundError: Если файл по указанному пути не найден.
        UnicodeDecodeError: Если файл не в кодировке UTF-8.
    """
    with open(filename, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        yield from reader
