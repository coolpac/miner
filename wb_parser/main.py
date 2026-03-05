#!/usr/bin/env python3
"""WB Parser — Парсер Wildberries для анализа товаров, цен и отзывов.

Использование:
    python main.py search "кроссовки" --pages 5 --sort popular --format excel
    python main.py product 12345678 87654321 --format csv
    python main.py feedbacks 12345678 --pages 10
    python main.py prices "наушники" --pages 3
"""

import argparse
import sys

from rich.console import Console
from rich.table import Table

from parser import WBParser

console = Console()


def cmd_search(args):
    """Поиск товаров по запросу."""
    wb = WBParser(proxy=args.proxy)
    products = wb.search_products(args.query, max_pages=args.pages, sort=args.sort)

    if not products:
        console.print("[red]Ничего не найдено[/red]")
        return

    _show_products_table(products[:20])

    if args.format == "excel":
        wb.export_to_excel(products, sheet_name="Поиск")
    elif args.format == "csv":
        wb.export_to_csv(products)
    else:
        wb.export_to_excel(products, sheet_name="Поиск")


def cmd_product(args):
    """Информация по конкретным артикулам."""
    wb = WBParser(proxy=args.proxy)
    products = wb.get_product_info(args.ids)

    if not products:
        console.print("[red]Товары не найдены[/red]")
        return

    _show_products_table(products)

    if args.format == "excel":
        wb.export_to_excel(products, sheet_name="Товары")
    elif args.format == "csv":
        wb.export_to_csv(products)


def cmd_feedbacks(args):
    """Парсинг отзывов."""
    wb = WBParser(proxy=args.proxy)
    feedbacks = wb.get_feedbacks(args.product_id, max_pages=args.pages)

    if not feedbacks:
        console.print("[red]Отзывы не найдены[/red]")
        return

    _show_feedbacks_table(feedbacks[:15])

    if args.format == "excel":
        wb.export_to_excel(feedbacks, sheet_name="Отзывы")
    elif args.format == "csv":
        wb.export_to_csv(feedbacks)


def cmd_prices(args):
    """Анализ цен конкурентов."""
    wb = WBParser(proxy=args.proxy)
    analysis = wb.compare_prices(args.query, max_pages=args.pages)

    if not analysis:
        console.print("[red]Данных нет[/red]")
        return

    table = Table(title="Анализ цен по брендам", show_lines=True)
    table.add_column("Бренд", style="cyan", max_width=25)
    table.add_column("Кол-во", justify="right")
    table.add_column("Мин. цена", justify="right", style="green")
    table.add_column("Макс. цена", justify="right", style="red")
    table.add_column("Сред. цена", justify="right", style="yellow")
    table.add_column("Рейтинг", justify="right")
    table.add_column("Отзывы", justify="right")

    for item in analysis[:30]:
        table.add_row(
            str(item["brand"]),
            str(item["count"]),
            f'{item["price_min"]:.0f}₽',
            f'{item["price_max"]:.0f}₽',
            f'{item["price_avg"]:.0f}₽',
            f'{item["rating_avg"]:.1f}',
            str(int(item["feedbacks_total"])),
        )

    console.print(table)

    if args.format == "excel":
        wb = WBParser()
        wb.export_to_excel(analysis, sheet_name="Анализ цен")
    elif args.format == "csv":
        wb = WBParser()
        wb.export_to_csv(analysis)


def _show_products_table(products: list[dict]):
    """Показать таблицу товаров в консоли."""
    table = Table(title="Товары Wildberries", show_lines=True)
    table.add_column("Артикул", style="cyan", justify="right")
    table.add_column("Название", max_width=35)
    table.add_column("Бренд", style="magenta", max_width=15)
    table.add_column("Цена", justify="right", style="green")
    table.add_column("Скидка", justify="right", style="red")
    table.add_column("Рейтинг", justify="right")
    table.add_column("Отзывы", justify="right")
    table.add_column("Остаток", justify="right")

    for p in products:
        table.add_row(
            str(p["id"]),
            p["name"][:35],
            p["brand"][:15],
            f'{p["price_sale"]:.0f}₽',
            f'{p["discount"]}%',
            f'{p["rating"]:.1f}',
            str(p["feedbacks"]),
            str(p["total_stock"]),
        )

    console.print(table)


def _show_feedbacks_table(feedbacks: list[dict]):
    """Показать таблицу отзывов в консоли."""
    table = Table(title="Отзывы", show_lines=True)
    table.add_column("Автор", style="cyan", max_width=15)
    table.add_column("Оценка", justify="center")
    table.add_column("Дата", max_width=12)
    table.add_column("Текст", max_width=50)

    for fb in feedbacks:
        stars = "★" * fb["rating"] + "☆" * (5 - fb["rating"])
        color = "green" if fb["rating"] >= 4 else "yellow" if fb["rating"] == 3 else "red"
        table.add_row(
            fb["author"][:15],
            f"[{color}]{stars}[/{color}]",
            fb["date"][:10] if fb["date"] else "",
            fb["text"][:50] if fb["text"] else "(без текста)",
        )

    console.print(table)


def main():
    p = argparse.ArgumentParser(
        description="WB Parser — Парсер Wildberries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python main.py search "кроссовки" --pages 5
  python main.py search "наушники" --sort priceup --format csv
  python main.py product 12345678 87654321
  python main.py feedbacks 12345678 --pages 10
  python main.py prices "кроссовки" --pages 3
        """,
    )
    p.add_argument("--proxy", help="HTTP прокси (http://user:pass@host:port)")

    sub = p.add_subparsers(dest="command", required=True)

    # search
    s = sub.add_parser("search", help="Поиск товаров")
    s.add_argument("query", help="Поисковый запрос")
    s.add_argument("--pages", type=int, default=3, help="Кол-во страниц (default: 3)")
    s.add_argument("--sort", default="popular", choices=["popular", "priceup", "pricedown", "rate", "newly"])
    s.add_argument("--format", default="excel", choices=["excel", "csv"])

    # product
    pr = sub.add_parser("product", help="Инфо по артикулам")
    pr.add_argument("ids", nargs="+", type=int, help="Артикулы товаров")
    pr.add_argument("--format", default="excel", choices=["excel", "csv"])

    # feedbacks
    fb = sub.add_parser("feedbacks", help="Отзывы на товар")
    fb.add_argument("product_id", type=int, help="Артикул товара")
    fb.add_argument("--pages", type=int, default=5, help="Кол-во страниц отзывов (default: 5)")
    fb.add_argument("--format", default="excel", choices=["excel", "csv"])

    # prices
    pc = sub.add_parser("prices", help="Анализ цен конкурентов")
    pc.add_argument("query", help="Поисковый запрос")
    pc.add_argument("--pages", type=int, default=3, help="Кол-во страниц (default: 3)")
    pc.add_argument("--format", default="excel", choices=["excel", "csv"])

    args = p.parse_args()

    commands = {
        "search": cmd_search,
        "product": cmd_product,
        "feedbacks": cmd_feedbacks,
        "prices": cmd_prices,
    }

    console.print("[bold]WB Parser v1.0[/bold] — Парсер Wildberries\n")
    commands[args.command](args)


if __name__ == "__main__":
    main()
