from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from reception.models import Guest


class GuestCRMProfile(models.Model):
    GUEST_TYPE_CHOICES = [
        ('REGULAR', 'Regular'),
        ('VIP', 'VIP'),
        ('CORPORATE', 'Corporate'),
        ('BLACKLISTED', 'Blacklisted'),
    ]

    guest = models.OneToOneField(Guest, on_delete=models.CASCADE, related_name='crm_profile')
    guest_type = models.CharField(max_length=30, choices=GUEST_TYPE_CHOICES, default='REGULAR')

    favorite_room = models.CharField(max_length=50, blank=True)
    favorite_food = models.CharField(max_length=150, blank=True)
    special_preference = models.TextField(blank=True)

    loyalty_points = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest.full_name} - {self.guest_type}"


class GuestComplaint(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='OPEN')
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolution_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


class GuestFeedback(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest.full_name} - {self.rating}/5"


class CorporateClient(models.Model):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    agreed_rate_note = models.TextField(blank=True)
    credit_allowed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name