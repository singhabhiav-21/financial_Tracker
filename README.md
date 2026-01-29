# FinTracker – Personal Finance Management System

FinTracker is a web-based personal finance management application that allows users to manage accounts, track transactions, and generate financial reports. The project was developed as part of academic coursework to demonstrate full-stack web development, backend architecture, and secure data handling.

**Live Demo**: [https://fintracker-kw1h.onrender.com](https://fintracker-kw1h.onrender.com)

**Demo Credentials:**
- Email: dummyaccount@mail.com
- Password: DemoPass1!

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
