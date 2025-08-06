# Overview

The Cash Flow Minimizer is a Flask-based web application that optimizes shared expense settlements using graph theory algorithms. The system calculates net balances between group members and minimizes the number of transactions needed to settle all debts. Users can create expense groups, add participants, track expenses, and generate optimized payment plans.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask**: Lightweight Python web framework chosen for its simplicity and rapid development capabilities
- **Jinja2 Templates**: Server-side rendering with template inheritance for consistent UI across pages
- **Bootstrap 5**: Frontend CSS framework with dark theme for responsive design and modern UI components

## Database Layer
- **SQLAlchemy ORM**: Object-relational mapping for database operations with declarative models
- **SQLite**: Default development database with configurable DATABASE_URL for production deployment
- **Connection Pooling**: Configured with pool recycling and pre-ping for connection reliability

## Data Models
- **ExpenseGroup**: Container for related expenses and people
- **Person**: Individual participants within expense groups
- **Expense**: Individual expense records with JSON-stored participant lists
- **Relationships**: Foreign key relationships between groups, people, and expenses with cascade deletion

## Core Algorithm
- **CashFlowOptimizer**: Graph theory implementation using min-heap algorithms
- **Net Balance Calculation**: Processes all expenses to determine who owes whom
- **Transaction Minimization**: Reduces settlement complexity by optimizing payment flows
- **Floating Point Precision**: Handles monetary calculations with proper rounding

## Frontend Architecture
- **Progressive Enhancement**: Basic functionality works without JavaScript
- **Real-time Calculations**: JavaScript for immediate expense split calculations
- **Bootstrap Components**: Modal dialogs, alerts, tooltips, and responsive layouts
- **Font Awesome Icons**: Consistent iconography throughout the interface

## Session Management
- **Flask Sessions**: Server-side session handling with configurable secret keys
- **Flash Messages**: User feedback system for form submissions and errors
- **CSRF Protection**: Implicit protection through Flask's session management

## Configuration Management
- **Environment Variables**: Database URL and session secrets configurable via environment
- **Development Defaults**: Fallback values for local development
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

# External Dependencies

## Python Packages
- **Flask**: Web framework and core functionality
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: WSGI utilities and middleware
- **SQLAlchemy**: Database abstraction layer

## Frontend Libraries
- **Bootstrap 5**: CSS framework loaded from Replit CDN with dark theme
- **Font Awesome 6**: Icon library loaded from CloudFlare CDN
- **Bootstrap JavaScript**: Component functionality for modals, alerts, and tooltips

## Database
- **SQLite**: Default file-based database for development
- **PostgreSQL**: Configurable via DATABASE_URL environment variable for production

## Development Tools
- **Python Logging**: Built-in logging module for debugging and monitoring
- **Flask Debug Mode**: Development server with auto-reload and enhanced error pages

## Deployment Considerations
- **Environment Variables**: DATABASE_URL for production database configuration
- **Session Security**: SESSION_SECRET for production session management
- **WSGI Compatibility**: Standard WSGI application structure for various deployment options