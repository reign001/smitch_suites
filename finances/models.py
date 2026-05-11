from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

from reception.models import Payment, GuestCharge
from restaurant.models import RestaurantOrder
from bar.models import BarSale


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('TRANSFER', 'Transfer'),
        ('POS', 'POS'),
        ('OTHER', 'Other'),
    ]

    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='CASH'
    )

    paid_to = models.CharField(max_length=150, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    expense_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FinancialTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    source = models.CharField(max_length=150)

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    reference = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class DailyFinanceReport(models.Model):
    report_date = models.DateField(unique=True)

    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    accommodation_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    restaurant_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bar_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    laundry_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.report_date)