"""Главный модуль парсера госзакупок.

Использование:
    python main.py search "разработка ПО" --pages 3
    python main.py search "уборка помещений" --fz 223 --pages 5
    python main.py monitor --categories it_services,cleaning --interval 3600
    python main.py export results.json --format xlsx
"""

import argparse
import json
import os
import sys
import time

from config import OUTPUT_DIR, MONITORED_CATEGORIES
from parser import search_tenders, get_tender_details


def cmd_search(args):
    """Поиск тендеров."""
    print(f"Поиск: '{args.query}' (ФЗ-{args.fz}, страниц: {args.pages})")
    tenders = search_tenders(args.query, fz=args.fz, pages=args.pages)

    if not tenders:
        print("Тендеры не найдены.")
        return

    print(f"\nНайдено тендеров: {len(tenders)}\n")
    for i, t in enumerate(tenders, 1):
        print(f"{i}. {t['number']}")
        print(f"   {t['name'][:100]}...")
        print(f"   Цена: {t['price']}")
        print(f"   Заказчик: {t['organization'][:80]}")
        print(f"   Срок: {t['date_deadline']}")
        print(f"   {t['link']}")
        print()

    # Сохранение результатов
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "tenders.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tenders, f, ensure_ascii=False, indent=2)
    print(f"Результаты сохранены в {output_file}")


def cmd_monitor(args):
    """Мониторинг новых тендеров по категориям."""
    categories = args.categories.split(",") if args.categories else list(MONITORED_CATEGORIES.keys())
    interval = args.interval
    seen_numbers = set()

    print(f"Мониторинг категорий: {', '.join(categories)}")
    print(f"Интервал проверки: {interval} сек")
    print("Нажмите Ctrl+C для остановки\n")

    try:
        while True:
            for cat in categories:
                query = MONITORED_CATEGORIES.get(cat, cat)
                print(f"[{time.strftime('%H:%M:%S')}] Проверка: {cat} ({query})")

                tenders = search_tenders(query, pages=1)
                new_tenders = [t for t in tenders if t["number"] not in seen_numbers]

                for t in new_tenders:
                    seen_numbers.add(t["number"])
                    print(f"  НОВЫЙ: {t['number']} — {t['name'][:80]}... ({t['price']})")

                if not new_tenders:
                    print(f"  Новых тендеров нет")

            print(f"\nСледующая проверка через {interval} сек...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")


def cmd_details(args):
    """Получение деталей тендера."""
    print(f"Загрузка деталей: {args.url}")
    details = get_tender_details(args.url)

    if not details:
        print("Не удалось получить детали.")
        return

    print(f"\nДокументы ({len(details.get('documents', []))}):")
    for doc in details.get("documents", []):
        print(f"  - {doc['name']}")

    print(f"\nЛоты ({len(details.get('lots', []))}):")
    for lot in details.get("lots", []):
        print(f"  - {lot['name']}: {lot['price']}")


def main():
    parser = argparse.ArgumentParser(description="Парсер госзакупок (zakupki.gov.ru)")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # search
    sp_search = subparsers.add_parser("search", help="Поиск тендеров")
    sp_search.add_argument("query", help="Поисковый запрос")
    sp_search.add_argument("--pages", type=int, default=1, help="Количество страниц (по умолчанию: 1)")
    sp_search.add_argument("--fz", default="44", choices=["44", "223"], help="Федеральный закон (44 или 223)")

    # monitor
    sp_monitor = subparsers.add_parser("monitor", help="Мониторинг новых тендеров")
    sp_monitor.add_argument("--categories", help="Категории через запятую (например: it_services,cleaning)")
    sp_monitor.add_argument("--interval", type=int, default=3600, help="Интервал проверки в секундах (по умолчанию: 3600)")

    # details
    sp_details = subparsers.add_parser("details", help="Детали тендера по URL")
    sp_details.add_argument("url", help="URL тендера на zakupki.gov.ru")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "details":
        cmd_details(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
