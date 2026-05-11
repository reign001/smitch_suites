from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

from reception.models import Room, Booking, GuestCharge
from inventory.models import InventoryItem


class RoomCleaning(models.Model):
    STATUS_CHOICES = [
        ('DIRTY', 'Dirty'),
        ('IN_PROGRESS', 'Cleaning In Progress'),
        ('CLEANED', 'Cleaned'),
        ('INSPECTED', 'Inspected'),
        ('AVAILABLE', 'Available'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='cleaning_records')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DIRTY')

    cleaning_note = models.TextField(blank=True)
    inspection_note = models.TextField(blank=True)

    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    inspected_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room.room_number} - {self.status}"


class LaundryRequest(models.Model):
    STATUS_CHOICES = [
        ('COLLECTED', 'Collected'),
        ('WASHING', 'Washing'),
        ('IRONING', 'Ironing'),
        ('READY', 'Ready'),
        ('DELIVERED', 'Delivered'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='laundry_requests'
    )

    clothing_items = models.TextField()
    quantity = models.PositiveIntegerField(default=1)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COLLECTED')

    added_to_guest_bill = models.BooleanField(default=False)

    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Laundry - {self.booking.guest.full_name}"


class LostAndFound(models.Model):
    STATUS_CHOICES = [
        ('FOUND', 'Found'),
        ('RETURNED', 'Returned'),
        ('UNCLAIMED', 'Unclaimed'),
    ]

    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)

    item_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    found_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FOUND')

    found_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.item_name


class MaintenanceIssue(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    issue_title = models.CharField(max_length=200)
    description = models.TextField()

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.issue_title