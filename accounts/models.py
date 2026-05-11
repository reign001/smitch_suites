from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('MANAGER', 'Manager'),
        ('RECEPTIONIST', 'Receptionist'),
        ('RESTAURANT', 'Restaurant'),
        ('ACCOUNTANT', 'Accountant'),
        ('STORE_MANAGER', 'Store Manager'),
        ('HOUSE_KEEPER', 'House Keeper'),
        ('SALES_PERSON', 'Sales Person'),
    ]

    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RECEPTIONIST')
    is_staff_member = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.username