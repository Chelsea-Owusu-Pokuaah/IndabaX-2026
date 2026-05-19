# Data Transformation, Manipulation and Preparation in SQL – Tutorial Readme

A PostgreSQL training dataset based on Indomie noodle distribution across Ghana. The data covers product variants, distributors, orders, and deliveries, and includes realistic data quality issues for use in SQL exercises.

---

## Files

| File | Description |
|------|-------------|
| `docker-compose.yml` | Spins up PostgreSQL 16 and pgAdmin 4 |
| `indomie_ghana_seed.sql` | Creates and populates all four tables |
| `Environment Setup Guide.docx` | Step-by-step environment setup instructions |

---

## The Dataset

Four tables are created on startup:

**`product_variants`** – Six noodle variants (Onion Chicken, Beef, Chicken, Vegetable, Chilli Chicken, Prawn) with prices in GHS and pack sizes.

**`distributors`** – 40 distributors across Ghana. About 35% of names have minor inconsistencies, and region entries use varied formats by design. Six distributors have no orders, making them useful for LEFT JOIN exercises.

**`orders`** – 309 orders from January 2024 onward. Known issues embedded in the data include NULL quantities, duplicate rows, pack-level entries mixed in with carton-level entries, and inconsistent region values.

**`delivery_dates`** – Delivery records for about 85% of orders, with a mix of on-time, delayed, and pending statuses.

---

## Setup

See `Environment Setup Guide.docx` for full instructions covering both setup options (Docker and local pgAdmin).

**Quick start with Docker:**

```bash
docker compose up -d
```

PostgreSQL will be available on port `5432`. pgAdmin opens at http://localhost:5050 (`admin@admin.com` / `secret`). The seed file loads automatically on first run.

---

## Verifying the Load

```sql
SELECT 'product_variants' AS t, COUNT(*) FROM product_variants
UNION ALL
SELECT 'distributors',          COUNT(*) FROM distributors
UNION ALL
SELECT 'orders',                COUNT(*) FROM orders
UNION ALL
SELECT 'delivery_dates',        COUNT(*) FROM delivery_dates;
```

Expected counts: 6 / 40 / 309 / 263.