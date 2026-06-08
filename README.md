# BookingManagementSystem

BookingManagementSystem is a Django-powered ticketing platform designed to support both event and movie bookings with a polished user experience. The application connects authenticated users to event/movie listings, supports seat selection and booking, integrates Stripe for secure payments, and generates downloadable PDF tickets for completed transactions. It is designed as a maintainable Django project with a clear separation between presentation, business logic, and data models.

## Key Capabilities

- Customer account registration and login
- Event and movie catalog browsing
- Seat selection with booking flow
- Stripe checkout integration for payment transactions
- PDF ticket generation for confirmed bookings
- Email delivery of booking confirmations

## Prerequisites

- Python 3.13
- Django
- Stripe Python SDK
- ReportLab

## Installation

1. Open the project root:
   ```powershell
   cd /d d:\python_programs\django_app\one
   ```
2. Activate the virtual environment:
   ```powershell
   .venv\Scripts\activate
   ```
3. Install project dependencies:
   ```powershell
   python -m pip install django stripe pillow reportlab
   ```
4. Create a `.env` file in the project root with the required secret values:
   ```powershell
   Set-Content .env "DJANGO_SECRET_KEY=replace-this-with-a-secure-key"
   Add-Content .env "STRIPE_TEST_SECRET_KEY=sk_test_your_key_here"
   Add-Content .env "STRIPE_TEST_PUBLIC_KEY=pk_test_your_key_here"
   ```
5. Apply database migrations:
   ```powershell
   python manage.py migrate
   ```

## Repository Layout

- `manage.py` — Django project entrypoint
- `one/` — project settings, URLs, WSGI/ASGI
- `myapp/` — core application models, views, templates, URLs
- `templates/` — frontend templates used by Django views
- `static/` — static assets (CSS, JS, images)
- `media/` — user-uploaded media files
- `.gitignore` — Git ignore rules for local artifacts

## Project Architecture

The application is designed with separation of concerns in mind:

- Presentation layer: `templates/` and `static/` deliver the UI and styling.
- Application layer: `myapp/views.py` orchestrates user interaction, booking flow, and payment processing.
- Data layer: `myapp/models.py` defines events, movies, bookings, payments, and user profile entities.
- Integration layer: Stripe and PDF ticket generation are managed in dedicated workflows, keeping external service logic isolated.

## Functional Overview

BookingManagementSystem supports the following business flows:

- User account management: registration, authentication, and session handling.
- Catalog browsing: event/movie listings with detail pages and navigation.
- Booking workflow: seat selection, order creation, booking confirmation, and persistence.
- Payments: Stripe checkout integration for secure transaction handling.
- Ticketing: PDF ticket generation and email delivery for confirmed bookings.