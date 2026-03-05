# Scripts Collection

Коллекция скриптов для автоматизации, парсинга данных и пассивного заработка.

> **[План развития](PLAN.md)** — стратегия монетизации публичных данных через API-сервисы.

## Скрипты

### 1. [WB Parser](wb_parser/) — Парсер Wildberries
Парсинг товаров, цен, остатков и отзывов с Wildberries. Экспорт в Excel/CSV, анализ цен конкурентов.

```bash
cd wb_parser
pip install -r requirements.txt
python main.py search "кроссовки" --pages 5
```

### 2. [FunPay Tools](funpay_tools/) — Инструменты FunPay
Парсинг лотов, мониторинг цен, арбитраж на FunPay.

### 3. [GosZakupki Parser](goszakupki_parser/) — Парсер госзакупок
Мониторинг тендеров с zakupki.gov.ru. Фильтрация по категориям, уведомления о новых закупках.

### 4. [EGRUL Checker](egrul_checker/) — Проверка контрагентов
Проверка юрлиц по ИНН/ОГРН через данные ЕГРЮЛ. Массовая проверка, экспорт отчётов.
