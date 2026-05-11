from django import forms
from .models import MenuItem, RestaurantOrder, RestaurantOrderItem
from reception.models import Booking


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'category', 'selling_price', 'description', 'is_available']


class RestaurantOrderForm(forms.ModelForm):
    booking = forms.ModelChoiceField(
        queryset=Booking.objects.filter(status='CHECKED_IN'),
        required=False,
        empty_label='Select Lodging Guest if bill should go to room'
    )

    class Meta:
        model = RestaurantOrder
        fields = ['booking', 'customer_name', 'room_number', 'payment_status']


class RestaurantOrderItemForm(forms.ModelForm):
    class Meta:
        model = RestaurantOrderItem
        fields = ['menu_item', 'quantity']