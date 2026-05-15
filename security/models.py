from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from reception.models import Guest, Room


class VisitorLog(models.Model):
    visitor_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    id_number = models.CharField(max_length=100, blank=True)

    person_to_see = models.CharField(max_length=150)
    purpose = models.CharField(max_length=200)

    vehicle_plate_number = models.CharField(max_length=50, blank=True)

    checked_in_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.visitor_name


class SecurityIncident(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('THEFT', 'Theft'),
        ('FIGHT', 'Fight/Disturbance'),
        ('DAMAGE', 'Property Damage'),
        ('FRAUD', 'Fraud Attempt'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access'),
        ('MEDICAL', 'Medical Emergency'),
        ('FIRE', 'Fire Emergency'),
        ('OTHER', 'Other'),
    ]

    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    guest = models.ForeignKey(Guest, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)

    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action_taken = models.TextField(blank=True)

    incident_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BlacklistRecord(models.Model):
    PERSON_TYPE_CHOICES = [
        ('GUEST', 'Guest'),
        ('VISITOR', 'Visitor'),
        ('STAFF', 'Staff'),
        ('OTHER', 'Other'),
    ]

    person_type = models.CharField(max_length=20, choices=PERSON_TYPE_CHOICES)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    reason = models.TextField()
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class KeyCardLog(models.Model):
    ACTION_CHOICES = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('LOST', 'Lost'),
        ('REPLACED', 'Replaced'),
    ]

    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    guest = models.ForeignKey(Guest, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    note = models.TextField(blank=True)

    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.room}"


class PatrolLog(models.Model):
    area_checked = models.CharField(max_length=150)
    observation = models.TextField()
    issue_found = models.BooleanField(default=False)
    officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    patrol_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.area_checked