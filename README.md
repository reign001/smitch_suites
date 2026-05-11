# Smitch Suites

A modern hotel management and hospitality operations platform designed to streamline hotel administration, guest management, room booking, restaurant operations, inventory coordination, and revenue tracking.

Smitch Suites is built to help hotels efficiently manage daily hospitality operations through a centralized and scalable web-based system.

---

# Features

## Dashboard & Analytics

* Real-time hotel operation overview
* Total rooms statistics
* Current guest tracking
* Daily booking analytics
* Revenue monitoring
* Operational summaries

## Room Management

* Add, edit, and manage rooms
* Room categorization
* Room pricing management
* Room availability tracking
* Room occupancy status
* Maintenance status management

## Booking & Reservation System

* Guest reservation management
* Check-in and check-out handling
* Booking history tracking
* Booking status management
* Reservation calendar support

## Guest Management

* Guest profile management
* Contact information storage
* Booking history records
* Guest activity tracking
* Repeat guest management

## Restaurant & Bar Management

* Restaurant order tracking
* Food and beverage coordination
* Bar inventory management
* Sales recording
* Customer billing integration

## Inventory & Kitchen Management

* Kitchen inventory monitoring
* Product stock tracking
* Low-stock notifications
* Supply coordination
* Inventory movement management

## Financial Management

* Revenue tracking
* Expense monitoring
* Daily financial reports
* Transaction logging
* Billing support

## Staff & Administration

* Admin dashboard
* Role-based access control
* Staff operational management
* Secure authentication system
* Activity monitoring

---

# Technology Stack

## Backend

* Python
* Django
* Django ORM

## Frontend

* HTML5
* CSS3
* JavaScript

## Database

* PostgreSQL / SQLite (development)

## Deployment

* Render
* Gunicorn / Daphne

---

# Project Structure

```bash
smitch_suites/
│
├── dashboard/
├── rooms/
├── bookings/
├── guests/
├── restaurant/
├── bar/
├── kitchen/
├── inventory/
├── finance/
├── static/
├── templates/
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

---

# Installation Guide

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smitch_suites.git
cd smitch_suites
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment Variables

Create a `.env` file and add:

```env
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=your_database_url
ALLOWED_HOSTS=127.0.0.1,localhost
```

---

# Database Setup

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

---

# Run Development Server

```bash
python manage.py runserver
```

Application will be available at:

```bash
http://127.0.0.1:8000/
```

---

# Admin Access

Django admin panel:

```bash
http://127.0.0.1:8000/admin/
```

Use your superuser credentials to log in.

---

# Core Modules

| Module     | Description                                |
| ---------- | ------------------------------------------ |
| Dashboard  | System analytics and operational summaries |
| Rooms      | Room management and availability           |
| Bookings   | Reservation and occupancy management       |
| Guests     | Guest records and profiles                 |
| Restaurant | Restaurant operations and orders           |
| Bar        | Beverage and bar operations                |
| Kitchen    | Kitchen coordination and inventory         |
| Finance    | Revenue and financial tracking             |
| Inventory  | Product and supply management              |

---

# Authentication & Security

* Django authentication system
* CSRF protection
* Session-based authentication
* Role-based access control
* Secure password hashing

---

# Future Improvements

Planned future features include:

* Online payment integration
* Mobile responsive optimization
* QR code check-in system
* AI-powered analytics
* SMS and email notifications
* Real-time room service requests
* Staff attendance management
* Customer feedback system
* Multi-branch hotel management
* API integration for booking platforms

---

# Deployment

## Render Deployment

1. Push code to GitHub
2. Connect repository to Render
3. Add environment variables
4. Configure PostgreSQL database
5. Deploy web service

---

# Contributing

Contributions are welcome.

To contribute:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a pull request

---

# License

This project is licensed under the MIT License.

---

# Contact Information

## Smitch Suites

For support, partnerships, or inquiries:

* Email: [support@smitchsuites.com](mailto:support@smitchsuites.com)
* Website: [https://www.smitchsuites.com](https://www.smitchsuites.com)
* Phone: +234 XXX XXX XXXX

---

# About Smitch Suites

Smitch Suites is focused on delivering modern hospitality management solutions that simplify hotel operations, improve guest experience, and enhance operational efficiency through technology.
