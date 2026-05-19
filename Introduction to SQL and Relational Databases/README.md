# Introduction to SQL and Relational Databases
### GDSS Workshop — Day 2

This folder contains all materials for Day 1 of the GDSS SQL workshop. The session runs for 3 hours and covers the foundations of relational databases and SQL using PostgreSQL. It is designed to flow directly into Day 2: *Data Transformation, Manipulation, and Preparation in SQL*.

---

## Contents

| File | Description |
|---|---|
| `shopdb_workshop.sql` | Complete SQL script for the session — table setup, all teaching queries, exercises, and Day 2 preview queries |
| `SQL_Session_Outline.docx` | Detailed session outline with timings, module breakdown, and learning outcomes |
| `SQL_Facilitation_Presentation.pptx` | Facilitation PowerPoint presentation slides including basic definitions, exercises, and facilitation notes |
| `README.md` | This file |

---

## Session Overview

**Duration:** 3 hours  
**Level:** Beginner  
**Tool:** PostgreSQL 18 (pgAdmin)  
**Database:** `shopdb` — a fictional e-commerce store with 4 tables

| Time | Module |
|---|---|
| 0:00 – 0:15 | Welcome, Setup & Icebreaker |
| 0:15 – 0:45 | Module 1 — Relational Databases & Data Organisation |
| 0:45 – 1:15 | Module 2 — Tables, Data Types & Schema Design |
| 1:15 – 1:30 | Break |
| 1:30 – 2:10 | Module 3 — Introduction to SQL Queries |
| 2:10 – 2:40 | Module 4 — Query Style, Distinct, Aliasing & SQL Flavours |
| 2:40 – 2:55 | Module 5 — Hands-On Practice |
| 2:55 – 3:00 | Day 2 Preview & Close |

---

## The Workshop Dataset

The SQL script creates a database called `shopdb` with four tables:

```
customers ──< orders ──< order_items >── products
```

- **customers** — registered customers
- **products** — spanning Electronics, Accessories, and Furniture
- **orders** — orders with statuses: pending, shipped, delivered, cancelled
- **order_items** — linking orders to products (many-to-many)

---

## How to Run the SQL Script

1. Open **pgAdmin** and connect to your PostgreSQL server
2. Right-click **Databases → Create → Database**, name it `shopdb`, and save
3. Click on `shopdb` to select it
4. Open the **Query Tool** (Tools → Query Tool or `Alt+Shift+Q`)
5. Open `shopdb_workshop.sql` via **File → Open**
6. Run **Part 1** first to create and populate the tables (`F5` or the Run button)
7. Confirm the setup by checking the verification query at the bottom of Part 1 — you should see row counts of 8, 10, 12, and 17
8. Work through Parts 2–7 section by section during the session

---

## Learning Outcomes

By the end of this session, participants will be able to:

- Explain what a relational database is and how tables relate through keys
- Read a table schema and identify column types and constraints
- Explain the difference between primary keys and foreign keys
- Understand why NULL is not the same as zero or an empty string
- Write `SELECT` queries with `WHERE`, `ORDER BY`, `LIMIT`, and `OFFSET`
- Filter data using `=`, `!=`, `>`, `<`, `BETWEEN`, `IN`, `LIKE`, `ILIKE`, `IS NULL.`
- Combine filter conditions with `AND`, `OR`, and parentheses
- Remove duplicate results using `DISTINCT.`
- Rename columns and tables using aliases (`AS`)
- Write well-formatted, commented SQL
- Understand that SQL syntax varies across platforms (PostgreSQL, MySQL, BigQuery)

---

## Prerequisites

No prior SQL knowledge is required. Participants should have:

- PostgreSQL 16 installed (or access to a cloud PostgreSQL instance)
- pgAdmin installed and connected to a running PostgreSQL server
- Basic comfort using a computer and opening files

---

## Connection to Day 2

This session is designed to hand off cleanly to Day 2: *Data Transformation, Manipulation, and Preparation in SQL*. The same `shopdb` database is used in Day 2. By the end of Day 1, participants will have the schema knowledge and query foundations that Day 2 builds on directly — particularly for joining tables, casting data types, and aggregating results.

---

*Day 1 of 2 — GDSS SQL Workshop*
