from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from reception.models import Booking, GuestCharge
from inventory.models import InventoryItem


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Food'),
        ('DRINK', 'Drink'),
        ('SNACK', 'Snack'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} uses {self.inventory_item.name}"


class RestaurantOrder(models.Model):
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
        related_name='restaurant_orders'
    )

    customer_name = models.CharField(max_length=150, blank=True)
    room_number = models.CharField(max_length=20, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    added_to_guest_bill = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def __str__(self):
        if self.booking:
            return f"Restaurant Order - {self.booking.guest.full_name}"
        return f"Restaurant Order - {self.customer_name or 'Walk-in Customer'}"


class RestaurantOrderItem(models.Model):
    order = models.ForeignKey(RestaurantOrder, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.unit_price = self.menu_item.selling_price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"