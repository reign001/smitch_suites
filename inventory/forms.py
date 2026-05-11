from django import forms
from .models import InventoryItem, StockIn, StockOut


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'name',
            'category',
            'unit',
            'quantity_in_stock',
            'reorder_level',
            'unit_cost',
            'supplier',
            'description',
        ]


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = [
            'item',
            'quantity',
            'unit_cost',
            'supplier',
            'note',
        ]


class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockOut
        fields = [
            'item',
            'quantity',
            'department',
            'note',
        ]