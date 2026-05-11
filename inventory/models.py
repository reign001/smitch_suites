from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    UNIT_CHOICES = [
        ('PCS', 'Pieces'),
        ('KG', 'Kilogram'),
        ('LITRE', 'Litre'),
        ('PACK', 'Pack'),
        ('BOTTLE', 'Bottle'),
        ('BAG', 'Bag'),
        ('CARTON', 'Carton'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    quantity_in_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level
    @property
    def total_value(self):
        return self.quantity_in_stock * self.unit_cost

    def __str__(self):
        return self.name


class StockIn(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='stock_ins')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    date_received = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.item.quantity_in_stock += self.quantity
            self.item.unit_cost = self.unit_cost
            self.item.save()

    def __str__(self):
        return f"{self.item.name} + {self.quantity}"


class StockOut(models.Model):
    DEPARTMENT_CHOICES = [
        ('RECEPTION', 'Reception'),
        ('HOUSEKEEPING', 'Housekeeping'),
        ('KITCHEN', 'Kitchen'),
        ('BAR', 'Bar'),
        ('RESTAURANT', 'Restaurant'),
        ('MAINTENANCE', 'Maintenance'),
        ('SECURITY', 'Security'),
        ('MANAGEMENT', 'Management'),
        ('OTHER', 'Other'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='stock_outs')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    date_issued = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new and self.quantity > self.item.quantity_in_stock:
            raise ValueError("Cannot issue more than available stock.")

        super().save(*args, **kwargs)

        if is_new:
            self.item.quantity_in_stock -= self.quantity
            self.item.save()

    def __str__(self):
        return f"{self.item.name} - {self.quantity} to {self.department}"


class DepartmentRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'),
        ('ISSUED', 'Issued'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity_requested = models.DecimalField(max_digits=12, decimal_places=2)
    department = models.CharField(max_length=50, choices=StockOut.DEPARTMENT_CHOICES)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_requested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.department} requested {self.item.name}"