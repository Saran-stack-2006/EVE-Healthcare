
from django.contrib import admin
from .models import DiagnosticCentre, DiagnosticTest, Booking, Payment

admin.site.register(DiagnosticCentre)
admin.site.register(DiagnosticTest)
admin.site.register(Booking)
admin.site.register(Payment)