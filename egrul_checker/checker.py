"""Проверка контрагентов через ЕГРЮЛ ФНС."""

import time
import httpx
from config import HEADERS, FNS_EGRUL_URL, REQUEST_DELAY, MAX_RETRIES


def search_by_inn(inn: str) -> dict | None:
    """Поиск юрлица/ИП по ИНН.

    Args:
        inn: ИНН (10 цифр для юрлиц, 12 для ИП)

    Returns:
        Данные о компании или None
    """
    if not inn.isdigit() or len(inn) not in (10, 12):
        print(f"Некорректный ИНН: {inn} (должен быть 10 или 12 цифр)")
        return None

    return _search_egrul({"query": inn})


def search_by_ogrn(ogrn: str) -> dict | None:
    """Поиск по ОГРН/ОГРНИП.

    Args:
        ogrn: ОГРН (13 цифр) или ОГРНИП (15 цифр)

    Returns:
        Данные о компании или None
    """
    if not ogrn.isdigit() or len(ogrn) not in (13, 15):
        print(f"Некорректный ОГРН: {ogrn} (должен быть 13 или 15 цифр)")
        return None

    return _search_egrul({"query": ogrn})


def search_by_name(name: str, region: str = "") -> list[dict]:
    """Поиск по наименованию организации.

    Args:
        name: Название компании
        region: Код региона (например, "77" для Москвы)

    Returns:
        Список найденных компаний
    """
    params = {"query": name}
    if region:
        params["region"] = region

    result = _search_egrul(params)
    if isinstance(result, list):
        return result
    return [result] if result else []


def _search_egrul(params: dict) -> dict | list | None:
    """Отправка запроса к ЕГРЮЛ API.

    Процесс:
    1. POST запрос с query для получения token
    2. GET запрос с token для получения результатов
    """
    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(headers=HEADERS, timeout=30.0) as client:
                # Шаг 1: Получение токена
                response = client.post(FNS_EGRUL_URL, data=params)
                response.raise_for_status()
                data = response.json()

                token = data.get("t")
                if not token:
                    print(f"Не удалось получить токен: {data}")
                    return None

                # Шаг 2: Ожидание и получение результатов
                time.sleep(1.0)

                for check in range(10):
                    result_response = client.get(
                        f"{FNS_EGRUL_URL}search-result/{token}"
                    )
                    result_data = result_response.json()

                    status = result_data.get("status")
                    if status == "ready":
                        rows = result_data.get("rows", [])
                        return _parse_results(rows)

                    time.sleep(0.5)

                print("Таймаут ожидания результатов")
                return None

        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"Ошибка запроса (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))

    return None


def _parse_results(rows: list) -> dict | list | None:
    """Парсинг результатов поиска ЕГРЮЛ."""
    if not rows:
        return None

    results = []
    for row in rows:
        entity = {
            "inn": row.get("i", ""),
            "ogrn": row.get("o", ""),
            "name": row.get("n", ""),
            "full_name": row.get("c", ""),
            "address": row.get("a", ""),
            "registration_date": row.get("r", ""),
            "director": row.get("g", ""),
            "status": _parse_status(row.get("e", "")),
            "token": row.get("t", ""),
        }
        results.append(entity)

    return results[0] if len(results) == 1 else results


def _parse_status(status_code: str) -> str:
    """Расшифровка статуса организации."""
    statuses = {
        "": "Действующая",
        "1": "Ликвидирована",
        "2": "В процессе ликвидации",
        "3": "В процессе реорганизации",
        "4": "Банкротство",
        "5": "Исключена из ЕГРЮЛ",
    }
    return statuses.get(status_code, f"Неизвестный ({status_code})")


def batch_check(inn_list: list[str]) -> list[dict]:
    """Массовая проверка списка ИНН.

    Args:
        inn_list: Список ИНН для проверки

    Returns:
        Список результатов проверки
    """
    results = []
    total = len(inn_list)

    for i, inn in enumerate(inn_list, 1):
        print(f"[{i}/{total}] Проверка ИНН: {inn}")
        result = search_by_inn(inn)
        results.append({
            "inn": inn,
            "found": result is not None,
            "data": result,
        })
        if i < total:
            time.sleep(REQUEST_DELAY)

    return results
