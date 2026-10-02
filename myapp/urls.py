
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('centres/', views.DiagnosticCentreListView.as_view(), name='centres'),
    path('tests/', views.DiagnosticTestListView.as_view(), name='tests'),
    path("bookings/", views.BookingListView.as_view(), name="bookings"),
    path("payments/", views.create_payment, name="create-payment"),
    path("payments/webhook/",views.payment_webhook,name="payment-webhook"),
]