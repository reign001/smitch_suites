from django import forms

from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category',
            'title',
            'description',
            'amount',
            'payment_method',
            'paid_to',
        ]