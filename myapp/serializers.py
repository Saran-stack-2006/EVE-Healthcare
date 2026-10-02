
from rest_framework import serializers
from .models import DiagnosticCentre, DiagnosticTest,Booking,Payment


class DiagnosticTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticTest
        fields = ['id', 'name', 'description', 'price', 'centre']


class DiagnosticCentreSerializer(serializers.ModelSerializer):
    tests = DiagnosticTestSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosticCentre
        fields = ['id', 'name', 'location', 'address', 'tests']
        

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "amount",
            "status",
            "created_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "id",
            "event_id",
            "transaction_reference",
            "amount",
            "status",
            "created_at",
        ]
        
    def validate_amount(self, value):
       if value <= 0:
        raise serializers.ValidationError(
            "Amount must be greater than zero."
        )
       return value