# EVE Healthcare Backend API

## About the Project

EVE Healthcare is a backend project developed using Django and Django REST Framework. The main purpose of this project is to help users book appointments for diagnostic tests.

Users can create an account, log in, view available diagnostic centres and tests, and book appointments. The booking amount is calculated automatically based on the selected test. I also implemented a mock payment system to handle payment success and failure through a webhook.

## Technologies Used

* Python
* Django
* Django REST Framework
* SQLite
* Simple JWT for authentication
* Postman for API testing

## Features

* User registration and login
* JWT authentication to protect API endpoints
* View diagnostic centres and available tests
* Book appointments
* Automatically calculate the booking amount
* Initiate mock payments
* Update booking status based on payment results
* Handle successful and failed payments
* Prevent duplicate webhook events from being processed
* Test API functionality using automated tests

## How to Run the Project

1. Download the project and open the folder in your terminal.

2. Create and activate a Python virtual environment.

3. Install the required packages:

   `pip install django djangorestframework djangorestframework-simplejwt`

4. Run the database migrations:

   `python manage.py migrate`

5. Start the Django server:

   `python manage.py runserver`

Once the server starts, the API will be available at `http://127.0.0.1:8000/`.

## API Endpoints

| Method    | Endpoint             | Purpose                               |
| --------- | -------------------- | ------------------------------------- |
| POST      | `/signup/`           | Create a new user account             |
| POST      | `/login/`            | Log in and receive JWT tokens         |
| GET       | `/centres/`          | View diagnostic centres               |
| GET       | `/tests/`            | View available diagnostic tests       |
| GET, POST | `/bookings/`         | View bookings or create a new booking |
| POST      | `/payments/`         | Start a mock payment                  |
| POST      | `/payments/webhook/` | Process a payment result              |

For protected endpoints, log in first and use the access token in the Bearer Token authorization header.

## How the Payment Process Works

1. The user creates a booking, and its status is set to `PENDING`.
2. The user initiates a payment, which is also initially set to `PENDING`.
3. A webhook sends the payment result as either `SUCCESS` or `FAILED`.
4. If the payment succeeds, the payment status changes to `SUCCESS` and the booking status changes to `CONFIRMED`.
5. If the payment fails, both statuses are updated to `FAILED`.
6. If the same webhook event is received again, the system detects the duplicate event and avoids processing it again.

## Running the Tests

To run the automated tests, use:

`python manage.py test myapp`

The project includes four automated tests covering booking creation, payment initiation, successful payment processing, and duplicate webhook events.

## Security and Future Improvements

The payment system is currently a mock implementation created for this project. Before using it in a real application, the webhook should be secured with payment-provider signature verification. Production deployment would also require proper secret management, database configuration, and security settings.

## Database Design

The project uses SQLite to store user, diagnostic centre, test, booking, and payment information.

* User: Stores registered user details and authentication information.
* DiagnosticCentre: Stores the centre name, location, and address.
* DiagnosticTest: Stores the test name, description, price, and the diagnostic centre offering the test.
* Booking: Connects a user with a diagnostic test and stores the appointment date, amount, and booking status.
* Payment: Stores the booking reference, payment amount, transaction reference, payment status, and webhook event ID.

The relationships between these models help maintain the connection between users, appointments, tests, and payments.

## Example API Requests

### Create a Booking

POST `/bookings/`

Include a valid JWT access token in the Authorization header.

json
{
  "diagnostic_test": 1,
  "appointment_datetime": "2026-10-15T10:00:00+05:30"
}


The booking amount is calculated from the selected diagnostic test.

### Initiate a Mock Payment

POST`/payments/`

```json
{
  "booking_id": 1
}
```

The API creates a pending payment and returns its payment ID.

### Process a Payment Webhook

*POST* `/payments/webhook/`

json
{
  "event_id": "EVT_PAYMENT_001",
  "payment_id": 1,
  "status": "SUCCESS"
}


The webhook updates the payment and associated booking status. Repeated event IDs are detected to prevent duplicate processing.

The IDs in these examples are illustrative; use IDs that exist in your database when testing.

## Assumptions

* Users must log in before creating or viewing their own bookings.
* The booking amount comes from the selected diagnostic test's price.
* Payments are simulated; no real money is transferred.
* A successful payment confirms the booking, while a failed payment marks it as failed.
* Repeated webhook event IDs should not be processed again.

## Future Improvements

If I had more time, I would consider adding PostgreSQL for production use, API documentation with Swagger, pagination, structured logging, rate limiting, and stronger webhook security using payment-provider signature verification. I would also add more automated tests for invalid requests, authorization, and payment edge cases.

