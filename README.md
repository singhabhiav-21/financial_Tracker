# FinTracker – Personal Finance Management System
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)
![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat)

<img width="2048" height="1150" alt="Screenshot 2026-04-14 at 03 45 37" src="https://github.com/user-attachments/assets/4ff440ac-4b4a-466c-8469-d8c7624cb669" />

# FinTracker – Personal Finance Management System

FinTracker is a web-based personal finance management application built as a personal project to explore backend architecture, secure data handling and real-world deployment constraints.

**Live Demo**: [https://fintracker-kw1h.onrender.com]

- Email: dummyaccount@mail.com
- Password: DemoPass1!

## Running with Docker 

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
 
```bash
git clone https://github.com/your-username/fintracker.git
cd fintracker
# Create a .env file with your DB credentials, secret key, and optionally an exchange API key
docker compose up --build
```
 
App runs at **http://localhost:8000**.
 
```bash
docker compose down          # stop
docker compose down -v       # stop and wipe the database
```
 
---
 
## Running Locally (Without Docker)
 
### Prerequisites
- Python 3.10+
- A running MySQL instance
```bash
git clone https://github.com/your-username/fintracker.git
cd fintracker
pip install -r requirements.txt
```
 
Copy and fill in the `.env` file (see above), then point `DB_HOST` at your local MySQL host (e.g. `localhost`).
 
```bash
uvicorn main:app --reload
```
 
App runs at **http://localhost:8000**.
 
---

## Key Features

### Dashboard
- Account balance overview with currency conversion
- Weekly income vs expense charts (configurable range)
- Recent transaction history
- Summary statistics for balances, income, and expenses

### Account Management
- Create and manage multiple account types (savings, current, stocks, crypto, etc.)
- Multi-currency account support
- Update account details (balance, currency, platform)
- Secure account deletion with password confirmation

### Transaction Management
- Add, edit, and delete transactions
- Category-based organization
- Date-based filtering and search
- Duplicate transaction detection using transaction hashing

### CSV Import
- Bulk import of transactions from bank statements
- Flexible column mapping for common CSV formats
- Automatic duplicate prevention
- File validation and controlled parsing

### Financial Reports
- Monthly PDF report generation
- Summary metrics for income and expenses
- Daily income vs expense charts
- Merchant spending overview
- Full transaction listings

## Technology Stack

### Backend
- **FastAPI** – REST API development, request validation, async endpoints
- **Starlette** – Session handling, middleware, static file serving
- **MySQL** – Relational database with connection pooling
- **mysql-connector-python** – Direct SQL access using parameterized queries
- **Custom DAO Layer** – Clear separation between API logic and database operations
- **Pandas** – Transaction aggregation and financial analysis
- **ReportLab** – PDF report generation
- **Requests** – External API calls for currency exchange rates

### Authentication & Security
- Password hashing using salted SHA-256
- Session-based authentication with cookies
- Basic rate limiting for login attempts
- Parameterized SQL queries to prevent SQL injection
- File upload validation (type and size checks)

**Note:** Security mechanisms are implemented for educational purposes and are not intended for production financial systems.
## Known Limitations
- SHA-256 is not recommended for production password hashing — bcrypt would be the production choice
- Free tier on Render causes cold starts
- Exchange rates cached for 12 hours


### Frontend
- Vanilla JavaScript
- Chart.js for data visualization
- HTML5 / CSS3
- FastAPI StaticFiles and FileResponse for frontend delivery

### Deployment
- **Render** – Backend hosting
- **Filess.io** – Managed MySQL database hosting

## API Overview

### Authentication
- `POST /login`
- `POST /register`
- `POST /logout`
- `GET /auth/status`
- `GET /me`

### Accounts
- `GET /accounts`
- `POST /accounts`
- `PUT /accounts/{id}`
- `DELETE /accounts/{id}`

### Transactions
- `GET /transactions`
- `POST /transactions`
- `PUT /transactions/{id}`
- `DELETE /transactions/{id}`

### Reports & Analytics
- `GET /api/weekly-chart`
- `POST /api/reports/generate`
- `GET /api/reports/download`

## Database Design

- **Users** – Authentication and profile data
- **Accounts** – Financial accounts and balances
- **Transactions** – Transaction records with duplicate detection
- **Reports** – Generated monthly financial summaries

## Project Purpose

This project demonstrates:
- RESTful API design with FastAPI
- Manual SQL database interaction and DAO architecture
- Session-based authentication
- CSV data processing
- PDF generation
- External API integration
- Frontend data visualization
- Cloud deployment

## Future Improvements

- Budget tracking and alerts
- Syncing transactions to accounts
- Recurring transactions
- Export to CSV/Excel
- Advanced analytics and forecasting