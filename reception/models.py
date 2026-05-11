from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('STANDARD', 'Standard'),
        ('DELUXE', 'Deluxe'),
        ('EXECUTIVE', 'Executive'),
        ('SUITE', 'Suite'),
    ]

    ROOM_STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('RESERVED', 'Reserved'),
        ('DIRTY', 'Dirty'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=30, choices=ROOM_TYPE_CHOICES)
    price_per_night = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='AVAILABLE')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"


class Guest(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    id_type = models.CharField(max_length=100, blank=True)
    id_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELLED', 'Cancelled'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='bookings')
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings_created'
    )

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='PENDING')

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def balance(self):
        return self.total_amount - self.amount_paid

    def __str__(self):
        return f"{self.guest.full_name} - Room {self.room.room_number if self.room else 'N/A'}"


class CheckIn(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='checkin')
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checkins_done'
    )
    check_in_time = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Check-in: {self.booking.guest.full_name}"


class CheckOut(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='checkout')
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checkouts_done'
    )
    check_out_time = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Check-out: {self.booking.guest.full_name}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('TRANSFER', 'Bank Transfer'),
        ('POS', 'POS'),
        ('CARD', 'Card'),
        ('OTHER', 'Other'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_received'
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.guest.full_name} - ₦{self.amount}"


class RoomServiceRequest(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Food & Beverage'),
        ('HOUSEKEEPING', 'Housekeeping'),
        ('LAUNDRY', 'Laundry'),
        ('COMFORT', 'Guest Comfort'),
        ('MAINTENANCE', 'Maintenance'),
        ('TRANSPORT', 'Transportation'),
        ('BUSINESS', 'Business Service'),
        ('CONCIERGE', 'Concierge'),
        ('EMERGENCY', 'Emergency'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='room_service_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    request_title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_billable = models.BooleanField(default=True)
    added_to_guest_bill = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_title} - {self.booking.guest.full_name}"
    

class GuestCharge(models.Model):
    CHARGE_CATEGORY_CHOICES = [
        ('ROOM', 'Room'),
        ('RESTAURANT', 'Restaurant'),
        ('BAR', 'Bar'),
        ('ROOM_SERVICE', 'Room Service'),
        ('LAUNDRY', 'Laundry'),
        ('DAMAGE', 'Damage'),
        ('OTHER', 'Other'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='charges')
    category = models.CharField(max_length=30, choices=CHARGE_CATEGORY_CHOICES)
    item_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='guest_charges_added'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking.guest.full_name} - {self.item_name}"

    