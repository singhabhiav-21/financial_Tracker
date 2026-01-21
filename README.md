# FinTracker - Personal Finance Management System

A comprehensive web-based financial management application that helps you track accounts, transactions, and generate detailed financial reports.

**Live Demo**: [https://fintracker-kw1h.onrender.com](https://fintracker-kw1h.onrender.com)

email: dummyaccount@mail.com
password: DemoPass1!


## Features

### Dashboard
- Multi-currency support with real-time exchange rate conversion (USD, EUR, GBP, SEK, INR, JPY, CAD, AUD)
- Interactive weekly charts showing income vs expenses (2-18 weeks configurable)
- Account balance overview with automatic currency conversion
- Recent transaction history with intuitive visual design
- Real-time statistics including total balance, income, and expenses

### Account Management
- Create and manage multiple accounts (savings, current, stocks, crypto, etc.)
- Support for various account types and platforms
- Multi-currency account support
- Secure account deletion with password verification
- Update account details including balance, currency, and platform

### Transaction Management
- Add, edit, and delete transactions
- Automatic duplicate detection using transaction hashing
- Import transactions via CSV (bank statement format)
- Category-based organization
- Date-based filtering and search
- Transaction descriptions and notes

### CSV Import
- Bulk transaction import from bank statements
- Intelligent column detection and flexible parsing
- Automatic duplicate prevention
- Support for multiple CSV formats and delimiters
- Secure file validation and processing

### Financial Reports
- Automated PDF report generation for any month
- Comprehensive executive summary with key metrics
- Visual charts showing daily income vs expenses
- Top merchant spending breakdown
- Transaction extremes (largest/smallest)
- Complete transaction listings
- Professional PDF layout with charts and tables

### Security
- Secure authentication with password hashing (SHA-256 + salt)
- Session-based user management
- Rate limiting for login attempts (5 attempts per 15 minutes)
- Password requirements: 8+ characters, uppercase, lowercase, numbers, special characters
- Secure file upload validation
- SQL injection prevention via parameterized queries

## Technology Stack

### Backend
- FastAPI - Modern Python web framework
- MySQL - Relational database with connection pooling
- Pandas - Data processing and analysis
- ReportLab - PDF report generation
- Requests - External API integration

### Frontend
- Vanilla JavaScript - No framework dependencies
- Chart.js - Interactive data visualizations
- HTML5/CSS3 - Responsive design
- Session Storage - Client-side state management

### External APIs
- ExchangeRate-API - Real-time currency conversion

### Deployment
- Render - Backend application hosting
- Filess.io - MySQL database hosting

### Database Management
- MySQL Connection Pooling - Efficient database connection management for improved performance and scalability

## Project Structure


The application follows a modular architecture with clear separation between backend logic, database operations, and frontend interfaces.

- main.py contains the FastAPI application with all API routes and endpoints
- databaseDAO directory handles all database operations including user authentication, account management, and transaction processing
- Visuals directory contains services for currency conversion, chart data processing, and PDF report generation
- frontend directory contains all HTML templates and JavaScript files for the user interface

## API Endpoints

### Authentication
- POST /login - User login
- POST /register - User registration
- POST /logout - User logout
- GET /auth/status - Check authentication status
- GET /me - Get current user info

### Accounts
- GET /accounts - List all accounts
- GET /accounts/{id} - Get specific account
- POST /accounts - Create new account
- PUT /accounts/{id} - Update account
- DELETE /accounts/{id} - Delete account

### Transactions
- GET /transactions - List all transactions
- GET /transactions/{id} - Get specific transaction
- POST /transactions - Create transaction
- PUT /transactions/{id} - Update transaction
- DELETE /transactions/{id} - Delete transaction

### Currency and Analytics
- GET /api/currency/dashboard - Dashboard with currency conversion
- GET /api/currency/rates - Get exchange rates
- GET /api/weekly-chart - Weekly income/expense data

### CSV Import
- POST /import-csv - Import transactions from CSV

### Reports
- GET /api/reports - List all reports
- GET /api/reports/{id} - Get report details
- POST /api/reports/generate - Generate new report
- GET /api/reports/download - Download PDF report
- DELETE /api/reports/{id} - Delete report

## Database Schema


The database consists of four main tables that store user information, accounts, transactions, and generated reports.

### Users Table
Stores user authentication and profile information including user ID, name, email, hashed password, and registration date.

### Account Table
Manages financial accounts with details such as account name, type, balance, currency, and associated platform.

### Transactions Table
Records all financial transactions with amount, description, date, and includes transaction hashing for duplicate detection.

### Reports Table
Tracks generated monthly reports with spending totals and transaction counts.

## Security Features

- Password Hashing: SHA-256 with random salt
- Session Management: Secure cookie-based sessions
- Rate Limiting: Login attempt restrictions
- SQL Injection Prevention: Parameterized queries
- File Upload Security: Type validation, size limits, malicious content detection
- XSS Protection: HTML escaping on frontend
- CORS Configuration: Controlled cross-origin access

## Usage Examples

### CSV Import Format
Your CSV file should have these columns with flexible matching: Value date, Text, Amount, and optionally Balance.

### Generating a Monthly Report
Navigate to Reports page, select month in YYYY-MM format, click Generate Report, and download the generated PDF.

### Multi-Currency Setup
Create accounts in different currencies, select your preferred display currency in the dashboard, and all balances automatically convert in real-time.

## Project Purpose

This is a student project developed to demonstrate full-stack web development skills including:
- RESTful API design with FastAPI
- Database design and SQL operations with MySQL connection pooling for efficient resource management
- User authentication and session management
- Real-time data visualization
- PDF generation and reporting
- Currency conversion and external API integration
- Secure file upload handling
- Responsive frontend design
- Cloud deployment using Render for backend hosting and Filess.io for database hosting

## Future Improvements

Planned features include budget tracking and alerts, recurring transaction support, mobile app development, export to Excel/CSV, advanced analytics and forecasting, and multi-user collaboration features.

---

Built using FastAPI, MySQL, and modern web technologies as part of academic coursework.
