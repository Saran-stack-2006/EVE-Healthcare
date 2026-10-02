
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .models import DiagnosticCentre, DiagnosticTest,Booking,Payment
from rest_framework import generics
from .serializers import (
    DiagnosticCentreSerializer,
    DiagnosticTestSerializer,
    BookingSerializer,
    PaymentSerializer,
)
import uuid

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Booking, Payment
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, Payment

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not username or not email or not password:
        return Response(
            {'error': 'Username, email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 8:
        return Response(
            {'error': 'Password must contain at least 8 characters.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email__iexact=email).exists():
        return Response(
            {'error': 'Email already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
    except IntegrityError:
        return Response(
            {'error': 'Could not create account. Try again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {'message': 'User registered successfully.'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Invalid username or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'Login successful.',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'username': user.username
    })
    
    
class DiagnosticCentreListView(generics.ListAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer
    permission_classes = [AllowAny]


class DiagnosticTestListView(generics.ListAPIView):
    queryset = DiagnosticTest.objects.select_related('centre').all()
    serializer_class = DiagnosticTestSerializer
    permission_classes = [AllowAny]
    

class BookingListView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Please log in using your access token.")
        return Booking.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        diagnostic_test = serializer.validated_data["diagnostic_test"]

        serializer.save(
            user=self.request.user,
            amount=diagnostic_test.price,
            status="PENDING",
        )






@api_view(["POST"])
@permission_classes([AllowAny])
def payment_webhook(request):
    event_id = request.data.get("event_id")
    payment_id = request.data.get("payment_id")
    outcome = request.data.get("status")

    if (
        not isinstance(event_id, str)
        or not event_id.strip()
        or payment_id is None
        or outcome not in ["SUCCESS", "FAILED"]
    ):
        return Response(
            {
                "error": (
                    "event_id, payment_id, and status "
                    "(SUCCESS or FAILED) are required."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payment_id = int(payment_id)
        if payment_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response(
            {"error": "payment_id must be a positive integer."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            # Lock the payment while processing this event.
            payment = Payment.objects.select_for_update().get(
                id=payment_id
            )

            # Check for an already processed event.
            if Payment.objects.filter(event_id=event_id).exists():
                return Response(
                    {"message": "Event already processed."},
                    status=status.HTTP_200_OK
                )

            # Do not change an already-finalized payment.
            if payment.status != Payment.Status.PENDING:
                return Response(
                    {"error": "Payment has already been finalized."},
                    status=status.HTTP_409_CONFLICT
                )

            # Store the event ID to support duplicate detection.
            payment.event_id = event_id
            payment.status = (
                Payment.Status.SUCCESS
                if outcome == "SUCCESS"
                else Payment.Status.FAILED
            )
            payment.save(update_fields=["event_id", "status"])

            booking = payment.booking
            booking.status = (
                Booking.Status.CONFIRMED
                if outcome == "SUCCESS"
                else Booking.Status.FAILED
            )
            booking.save(update_fields=["status"])

        return Response(
            {
                "message": "Webhook processed successfully.",
                "event_id": event_id,
                "payment_status": payment.status,
                "booking_status": booking.status
            },
            status=status.HTTP_200_OK
        )

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found."},
            status=status.HTTP_404_NOT_FOUND
        )



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment(request):
    booking_id = request.data.get("booking_id")

    if not booking_id:
        return Response(
            {"error": "booking_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        booking = Booking.objects.get(
            id=booking_id,
            user=request.user
        )
    except (Booking.DoesNotExist, ValueError, TypeError):
        return Response(
            {"error": "Booking not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if booking.status != Booking.Status.PENDING:
        return Response(
            {"error": "Booking is not pending."},
            status=status.HTTP_400_BAD_REQUEST
        )

    payment = Payment.objects.create(
        booking=booking,
        amount=booking.amount,
        status=Payment.Status.PENDING,
        transaction_reference=f"MOCK-{uuid.uuid4().hex[:12].upper()}"
    )

    return Response(
        {
            "message": "Mock payment initiated.",
            "payment_id": payment.id,
            "booking_id": booking.id,
            "amount": str(payment.amount),
            "payment_status": payment.status,
            "booking_status": booking.status,
            "transaction_reference": payment.transaction_reference
        },
        status=status.HTTP_201_CREATED
    )