from django import forms
from .models import GuestCRMProfile, GuestComplaint, GuestFeedback, CorporateClient


class GuestCRMProfileForm(forms.ModelForm):
    class Meta:
        model = GuestCRMProfile
        fields = [
            'guest_type',
            'favorite_room',
            'favorite_food',
            'special_preference',
            'loyalty_points',
            'notes',
        ]


class GuestComplaintForm(forms.ModelForm):
    class Meta:
        model = GuestComplaint
        fields = [
            'guest',
            'title',
            'description',
            'status',
            'resolution_note',
        ]


class GuestFeedbackForm(forms.ModelForm):
    class Meta:
        model = GuestFeedback
        fields = [
            'guest',
            'rating',
            'comment',
        ]


class CorporateClientForm(forms.ModelForm):
    class Meta:
        model = CorporateClient
        fields = [
            'company_name',
            'contact_person',
            'phone',
            'email',
            'address',
            'agreed_rate_note',
            'credit_allowed',
        ]