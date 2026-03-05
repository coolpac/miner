"""Основной модуль парсинга Wildberries."""

import os
import time
from datetime import datetime
from typing import Optional

import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from api import WBApi
from config import MAX_PAGES, DEFAULT_OUTPUT_DIR

console = Console()


class WBParser:
    """Парсер товаров Wildberries."""

    def __init__(self, proxy: Optional[str] = None):
        self.api = WBApi(proxy=proxy)

    @staticmethod
    def _extract_product(p: dict) -> dict:
        """Извлечь данные товара из JSON ответа API."""
        price_basic = p.get("priceU", 0) / 100
        price_sale = p.get("salePriceU", 0) / 100
        discount = p.get("sale", 0)

        # Подсчёт общего остатка по всем складам
        total_stock = 0
        sizes = p.get("sizes", [])
        for size in sizes:
            for stock in size.get("stocks", []):
                total_stock += stock.get("qty", 0)

        # Размеры в наличии
        available_sizes = [
            s.get("name", s.get("origName", ""))
            for s in sizes
            if any(st.get("qty", 0) > 0 for st in s.get("stocks", []))
        ]

        return {
            "id": p.get("id"),
            "name": p.get("name", ""),
            "brand": p.get("brand", ""),
            "brand_id": p.get("brandId"),
            "supplier": p.get("supplier", ""),
            "supplier_id": p.get("supplierId"),
            "supplier_rating": p.get("supplierRating", 0),
            "price_basic": price_basic,
            "price_sale": price_sale,
            "discount": discount,
            "rating": p.get("reviewRating", 0),
            "feedbacks": p.get("feedbacks", 0),
            "total_stock": total_stock,
            "available_sizes": ", ".join(available_sizes) if available_sizes else "Без размеров",
            "colors": ", ".join(c.get("name", "") for c in p.get("colors", [])),
            "url": f"https://www.wildberries.ru/catalog/{p.get('id')}/detail.aspx",
        }

    def search_products(self, query: str, max_pages: int = 5, sort: str = "popular") -> list[dict]:
        """Поиск товаров по запросу с пагинацией."""
        all_products = []
        pages = min(max_pages, MAX_PAGES)

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold]{task.completed}/{task.total} стр."),
            console=console,
        ) as progress:
            task = progress.add_task(f'Поиск: "{query}"', total=pages)

            for page in range(1, pages + 1):
                data = self.api.search(query, page=page, sort=sort)
                if not data:
                    break

                products = data.get("data", {}).get("products", [])
                if not products:
                    break

                for p in products:
                    all_products.append(self._extract_product(p))

                progress.update(task, advance=1)

        console.print(f"[green]Найдено {len(all_products)} товаров по запросу \"{query}\"[/green]")
        return all_products

    def get_product_info(self, product_ids: list[int]) -> list[dict]:
        """Получить информацию по конкретным товарам (по артикулам)."""
        all_products = []

        # Разбиваем на батчи по 100
        batches = [product_ids[i:i + 100] for i in range(0, len(product_ids), 100)]

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold]{task.completed}/{task.total}"),
            console=console,
        ) as progress:
            task = progress.add_task("Загрузка товаров", total=len(batches))

            for batch in batches:
                data = self.api.get_product_detail(batch)
                if data:
                    products = data.get("data", {}).get("products", [])
                    for p in products:
                        all_products.append(self._extract_product(p))
                progress.update(task, advance=1)

        console.print(f"[green]Загружено {len(all_products)} товаров[/green]")
        return all_products

    def get_feedbacks(self, product_id: int, max_pages: int = 5) -> list[dict]:
        """Получить отзывы на товар."""
        all_feedbacks = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold]{task.completed}/{task.total} стр."),
            console=console,
        ) as progress:
            task = progress.add_task(f"Отзывы для {product_id}", total=max_pages)

            for page in range(1, max_pages + 1):
                data = self.api.get_feedbacks(product_id, page=page)
                if not data:
                    break

                feedbacks = data.get("feedbacks", [])
                if not feedbacks:
                    break

                for fb in feedbacks:
                    all_feedbacks.append({
                        "product_id": product_id,
                        "author": fb.get("wbUserDetails", {}).get("name", "Аноним"),
                        "rating": fb.get("productValuation", 0),
                        "date": fb.get("createdDate", ""),
                        "text": fb.get("text", ""),
                        "pros": fb.get("pros", ""),
                        "cons": fb.get("cons", ""),
                        "answer": fb.get("answer", {}).get("text", "") if fb.get("answer") else "",
                        "photos_count": len(fb.get("photoLinks", [])),
                    })

                progress.update(task, advance=1)

        console.print(f"[green]Загружено {len(all_feedbacks)} отзывов[/green]")
        return all_feedbacks

    @staticmethod
    def export_to_excel(data: list[dict], filename: str = None, sheet_name: str = "Данные") -> str:
        """Экспорт данных в Excel файл."""
        if not data:
            console.print("[yellow]Нет данных для экспорта[/yellow]")
            return ""

        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wb_data_{timestamp}.xlsx"

        filepath = os.path.join(DEFAULT_OUTPUT_DIR, filename)
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, sheet_name=sheet_name, engine="openpyxl")

        console.print(f"[green]Сохранено в {filepath} ({len(data)} строк)[/green]")
        return filepath

    @staticmethod
    def export_to_csv(data: list[dict], filename: str = None) -> str:
        """Экспорт данных в CSV файл."""
        if not data:
            console.print("[yellow]Нет данных для экспорта[/yellow]")
            return ""

        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wb_data_{timestamp}.csv"

        filepath = os.path.join(DEFAULT_OUTPUT_DIR, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")

        console.print(f"[green]Сохранено в {filepath} ({len(data)} строк)[/green]")
        return filepath

    def compare_prices(self, query: str, max_pages: int = 3) -> list[dict]:
        """Анализ цен конкурентов: группировка по бренду с мин/макс/средней ценой."""
        products = self.search_products(query, max_pages=max_pages)
        if not products:
            return []

        df = pd.DataFrame(products)
        analysis = df.groupby("brand").agg(
            count=("id", "count"),
            price_min=("price_sale", "min"),
            price_max=("price_sale", "max"),
            price_avg=("price_sale", "mean"),
            rating_avg=("rating", "mean"),
            feedbacks_total=("feedbacks", "sum"),
        ).reset_index()

        analysis["price_avg"] = analysis["price_avg"].round(2)
        analysis["rating_avg"] = analysis["rating_avg"].round(2)
        analysis = analysis.sort_values("count", ascending=False)

        result = analysis.to_dict("records")
        console.print(f"[green]Анализ цен: {len(result)} брендов[/green]")
        return result
