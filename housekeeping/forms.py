from django import forms

from .models import (
    RoomCleaning,
    LaundryRequest,
    LostAndFound,
    MaintenanceIssue
)


class RoomCleaningForm(forms.ModelForm):
    class Meta:
        model = RoomCleaning
        fields = [
            'room',
            'assigned_to',
            'priority',
            'cleaning_note',
        ]


class LaundryRequestForm(forms.ModelForm):
    class Meta:
        model = LaundryRequest
        fields = [
            'booking',
            'clothing_items',
            'quantity',
            'amount',
        ]


class LostAndFoundForm(forms.ModelForm):
    class Meta:
        model = LostAndFound
        fields = [
            'room',
            'booking',
            'item_name',
            'description',
        ]


class MaintenanceIssueForm(forms.ModelForm):
    class Meta:
        model = MaintenanceIssue
        fields = [
            'room',
            'issue_title',
            'description',
            'priority',
        ]