from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from reception.models import Booking, GuestCharge
from inventory.models import InventoryItem


class BarItem(models.Model):
    CATEGORY_CHOICES = [
        ('BEER', 'Beer'),
        ('WINE', 'Wine'),
        ('SPIRIT', 'Spirit'),
        ('SOFT_DRINK', 'Soft Drink'),
        ('WATER', 'Water'),
        ('ENERGY_DRINK', 'Energy Drink'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BarSale(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('ADDED_TO_ROOM', 'Added to Guest Room'),
        ('UNPAID', 'Unpaid'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bar_sales'
    )

    customer_name = models.CharField(max_length=150, blank=True)
    room_number = models.CharField(max_length=20, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='PAID')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    added_to_guest_bill = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def __str__(self):
        return f"Bar Sale #{self.id}"


class BarSaleItem(models.Model):
    sale = models.ForeignKey(BarSale, on_delete=models.CASCADE, related_name='items')
    bar_item = models.ForeignKey(BarItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.unit_price = self.bar_item.selling_price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bar_item.name} x {self.quantity}"