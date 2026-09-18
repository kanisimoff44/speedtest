#!/usr/bin/env python3
"""Замер скорости интернета: N последовательных GET-запросов к URL."""

import argparse
import sys
import time
import urllib.error
import urllib.request

CHUNK = 64 * 1024


def download(url: str, timeout: float) -> tuple[int, float]:
    """Скачивает ответ целиком, возвращает (байт, секунд)."""
    req = urllib.request.Request(url, headers={"User-Agent": "speedtest/1.0", "Cache-Control": "no-cache"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total = 0
        while chunk := resp.read(CHUNK):
            total += len(chunk)
    return total, time.perf_counter() - start


def main() -> int:
    parser = argparse.ArgumentParser(description="Замер скорости скачивания по URL.")
    parser.add_argument("url", help="адрес тяжёлого файла (например, картинки)")
    parser.add_argument("-n", "--requests", type=int, default=10, help="число запросов (по умолчанию 10)")
    parser.add_argument("-t", "--timeout", type=float, default=60, help="таймаут одного запроса, сек")
    args = parser.parse_args()

    times: list[float] = []
    total_bytes = 0

    for i in range(1, args.requests + 1):
        try:
            size, elapsed = download(args.url, args.timeout)
        except (urllib.error.URLError, OSError) as e:
            print(f"[{i}/{args.requests}] ошибка: {e}", file=sys.stderr)
            continue
        times.append(elapsed)
        total_bytes += size
        print(f"[{i}/{args.requests}] {size / 1e6:.2f} МБ за {elapsed:.3f} с  ({size / 1e6 / elapsed:.2f} МБ/с)")

    if not times:
        print("Ни один запрос не выполнился успешно.", file=sys.stderr)
        return 1

    total_time = sum(times)
    print()
    print(f"Успешных запросов:     {len(times)} из {args.requests}")
    print(f"Среднее время запроса: {total_time / len(times):.3f} с")
    print(f"Скачано всего:         {total_bytes / 1e6:.2f} МБ")
    print(f"Средняя скорость:      {total_bytes / 1e6 / total_time:.2f} МБ/с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
