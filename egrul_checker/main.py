"""Главный модуль проверки контрагентов.

Использование:
    python main.py check 7707083893
    python main.py check --ogrn 1027700132195
    python main.py search "Сбербанк" --region 77
    python main.py batch inn_list.txt
    python main.py batch inn_list.txt --export xlsx
"""

import argparse
import json
import os
import sys

from config import OUTPUT_DIR
from checker import search_by_inn, search_by_ogrn, search_by_name, batch_check


def cmd_check(args):
    """Проверка одного контрагента."""
    if args.ogrn:
        print(f"Поиск по ОГРН: {args.ogrn}")
        result = search_by_ogrn(args.ogrn)
    else:
        inn = args.query
        print(f"Поиск по ИНН: {inn}")
        result = search_by_inn(inn)

    if not result:
        print("Организация не найдена.")
        return

    _print_entity(result)


def cmd_search(args):
    """Поиск по названию."""
    print(f"Поиск: '{args.query}'")
    if args.region:
        print(f"Регион: {args.region}")

    results = search_by_name(args.query, region=args.region or "")

    if not results:
        print("Ничего не найдено.")
        return

    print(f"\nНайдено: {len(results)}\n")
    for i, entity in enumerate(results if isinstance(results, list) else [results], 1):
        print(f"--- {i} ---")
        _print_entity(entity)
        print()


def cmd_batch(args):
    """Массовая проверка из файла."""
    if not os.path.exists(args.file):
        print(f"Файл не найден: {args.file}")
        return

    with open(args.file, "r", encoding="utf-8") as f:
        inn_list = [line.strip() for line in f if line.strip()]

    print(f"Загружено ИНН: {len(inn_list)}")
    results = batch_check(inn_list)

    # Статистика
    found = sum(1 for r in results if r["found"])
    print(f"\nИтого: {found}/{len(results)} найдено")

    # Проблемные
    not_found = [r["inn"] for r in results if not r["found"]]
    if not_found:
        print(f"Не найдены: {', '.join(not_found)}")

    # Ликвидированные
    liquidated = [
        r["inn"] for r in results
        if r["found"] and r["data"] and r["data"].get("status") != "Действующая"
    ]
    if liquidated:
        print(f"Недействующие: {', '.join(liquidated)}")

    # Сохранение
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "batch_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nРезультаты сохранены в {output_file}")

    # Экспорт в Excel
    if args.export == "xlsx":
        _export_xlsx(results)


def _print_entity(entity: dict):
    """Вывод информации об организации."""
    if isinstance(entity, list):
        for e in entity:
            _print_entity(e)
        return

    print(f"  Наименование: {entity.get('name', '—')}")
    print(f"  Полное имя:   {entity.get('full_name', '—')}")
    print(f"  ИНН:          {entity.get('inn', '—')}")
    print(f"  ОГРН:         {entity.get('ogrn', '—')}")
    print(f"  Адрес:        {entity.get('address', '—')}")
    print(f"  Руководитель: {entity.get('director', '—')}")
    print(f"  Дата рег.:    {entity.get('registration_date', '—')}")
    print(f"  Статус:       {entity.get('status', '—')}")


def _export_xlsx(results: list):
    """Экспорт результатов в Excel."""
    try:
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Проверка контрагентов"

        # Заголовки
        headers = ["ИНН", "Найден", "Наименование", "ОГРН", "Адрес", "Руководитель", "Статус"]
        ws.append(headers)

        for r in results:
            data = r.get("data") or {}
            ws.append([
                r["inn"],
                "Да" if r["found"] else "Нет",
                data.get("name", ""),
                data.get("ogrn", ""),
                data.get("address", ""),
                data.get("director", ""),
                data.get("status", ""),
            ])

        output_file = os.path.join(OUTPUT_DIR, "batch_results.xlsx")
        wb.save(output_file)
        print(f"Excel-файл сохранён: {output_file}")
    except ImportError:
        print("Для экспорта в Excel установите: pip install openpyxl")


def main():
    parser = argparse.ArgumentParser(description="Проверка контрагентов (ЕГРЮЛ/ЕГРИП)")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # check
    sp_check = subparsers.add_parser("check", help="Проверка по ИНН или ОГРН")
    sp_check.add_argument("query", help="ИНН для проверки")
    sp_check.add_argument("--ogrn", help="Поиск по ОГРН вместо ИНН")

    # search
    sp_search = subparsers.add_parser("search", help="Поиск по названию")
    sp_search.add_argument("query", help="Название организации")
    sp_search.add_argument("--region", help="Код региона (77 = Москва, 78 = СПб)")

    # batch
    sp_batch = subparsers.add_parser("batch", help="Массовая проверка из файла")
    sp_batch.add_argument("file", help="Файл со списком ИНН (по одному на строку)")
    sp_batch.add_argument("--export", choices=["xlsx"], help="Формат экспорта")

    args = parser.parse_args()

    if args.command == "check":
        cmd_check(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "batch":
        cmd_batch(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
