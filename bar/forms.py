from django import forms
from .models import BarItem, BarSale, BarSaleItem
from reception.models import Booking


class BarItemForm(forms.ModelForm):
    class Meta:
        model = BarItem
        fields = ['name', 'category', 'inventory_item', 'selling_price', 'is_available']


class BarSaleForm(forms.ModelForm):
    booking = forms.ModelChoiceField(
        queryset=Booking.objects.filter(status='CHECKED_IN'),
        required=False,
        empty_label='Select Lodging Guest if bill should go to room'
    )

    class Meta:
        model = BarSale
        fields = ['booking', 'customer_name', 'room_number', 'payment_status']


class BarSaleItemForm(forms.ModelForm):
    class Meta:
        model = BarSaleItem
        fields = ['bar_item', 'quantity']