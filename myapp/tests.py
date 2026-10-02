
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from .models import DiagnosticCentre, DiagnosticTest, Booking, Payment


class HealthcareAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPass123!"
        )

        self.centre = DiagnosticCentre.objects.create(
            name="Test Diagnostic Centre",
            location="Coimbatore",
            address="Test Address"
        )

        self.test = DiagnosticTest.objects.create(
            centre=self.centre,
            name="Blood Test",
            description="Test blood sample",
            price="500.00"
        )

        self.client.force_authenticate(user=self.user)

    def test_create_booking(self):
        response = self.client.post(
            "/bookings/",
            {
                "diagnostic_test": self.test.id,
                "appointment_datetime": "2026-10-20T10:00:00+05:30"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")
        self.assertEqual(response.data["amount"], "500.00")

    def test_create_payment(self):
        booking = Booking.objects.create(
            user=self.user,
            diagnostic_test=self.test,
            appointment_datetime="2026-10-20T10:00:00Z",
            amount="500.00",
            status=Booking.Status.PENDING
        )

        response = self.client.post(
            "/payments/",
            {"booking_id": booking.id},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_status"], "PENDING")
        self.assertEqual(response.data["booking_status"], "PENDING")

    def test_webhook_success(self):
        booking = Booking.objects.create(
            user=self.user,
            diagnostic_test=self.test,
            appointment_datetime="2026-10-20T10:00:00Z",
            amount="500.00",
            status=Booking.Status.PENDING
        )

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.amount,
            status=Payment.Status.PENDING
        )

        response = self.client.post(
            "/payments/webhook/",
            {
                "event_id": "test-event-success",
                "payment_id": payment.id,
                "status": "SUCCESS"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment.refresh_from_db()
        booking.refresh_from_db()

        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_webhook_duplicate_event(self):
        booking = Booking.objects.create(
            user=self.user,
            diagnostic_test=self.test,
            appointment_datetime="2026-10-20T10:00:00Z",
            amount="500.00",
            status=Booking.Status.PENDING
        )

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.amount,
            status=Payment.Status.PENDING,
            event_id="duplicate-event"
        )

        response = self.client.post(
            "/payments/webhook/",
            {
                "event_id": "duplicate-event",
                "payment_id": payment.id,
                "status": "SUCCESS"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Event already processed."
        )