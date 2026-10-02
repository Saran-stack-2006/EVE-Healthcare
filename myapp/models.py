from django.db import models
from django.contrib.auth.models import User



class DiagnosticCentre(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class DiagnosticTest(models.Model):
    centre = models.ForeignKey(
        DiagnosticCentre,
        on_delete=models.CASCADE,
        related_name="tests"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.centre.name}"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diagnostic_test = models.ForeignKey(
        DiagnosticTest, on_delete=models.PROTECT
    )
    appointment_datetime = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.status}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    booking = models.ForeignKey(
        Booking,
        on_delete=models.PROTECT,
        related_name="payments"
    )
    event_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    transaction_reference = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
   