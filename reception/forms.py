from django import forms
from .models import Guest, Booking, Room


class BookingForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    gender = forms.ChoiceField(choices=Guest.GENDER_CHOICES, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    id_type = forms.CharField(max_length=100, required=False)
    id_number = forms.CharField(max_length=100, required=False)

    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(status='AVAILABLE'),
        empty_label="Select Available Room"
    )

    check_in_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    number_of_guests = forms.IntegerField(min_value=1, initial=1)
    amount_paid = forms.DecimalField(max_digits=12, decimal_places=2, initial=0)
    note = forms.CharField(widget=forms.Textarea, required=False)


from django import forms


class CheckInForm(forms.Form):
    additional_payment = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        initial=0
    )

    payment_method = forms.ChoiceField(
        choices=[
            ('CASH', 'Cash'),
            ('TRANSFER', 'Bank Transfer'),
            ('POS', 'POS'),
            ('CARD', 'Card'),
            ('OTHER', 'Other'),
        ],
        required=False
    )

    payment_reference = forms.CharField(max_length=100, required=False)

    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )


class CheckOutForm(forms.Form):
    final_payment = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        initial=0
    )

    payment_method = forms.ChoiceField(
        choices=[
            ('CASH', 'Cash'),
            ('TRANSFER', 'Bank Transfer'),
            ('POS', 'POS'),
            ('CARD', 'Card'),
            ('OTHER', 'Other'),
        ],
        required=False
    )

    payment_reference = forms.CharField(max_length=100, required=False)

    room_condition_note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Room Condition / Checkout Note'
    )

from .models import RoomServiceRequest, Booking


class RoomServiceRequestForm(forms.ModelForm):
    booking = forms.ModelChoiceField(
        queryset=Booking.objects.filter(status='CHECKED_IN'),
        empty_label='Select Current Guest / Room'
    )

    class Meta:
        model = RoomServiceRequest
        fields = [
            'booking',
            'category',
            'request_title',
            'description',
            'quantity',
            'unit_price',
            'is_billable',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }