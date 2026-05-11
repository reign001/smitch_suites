from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import (
    ExpenseCategory,
    Expense,
    FinancialTransaction,
    DailyFinanceReport
)

admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(FinancialTransaction)
admin.site.register(DailyFinanceReport)