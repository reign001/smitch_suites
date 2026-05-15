from django import forms
from .models import VisitorLog, SecurityIncident, BlacklistRecord, KeyCardLog, PatrolLog


class VisitorLogForm(forms.ModelForm):
    class Meta:
        model = VisitorLog
        fields = [
            'visitor_name',
            'phone',
            'id_number',
            'person_to_see',
            'purpose',
            'vehicle_plate_number',
        ]


class SecurityIncidentForm(forms.ModelForm):
    class Meta:
        model = SecurityIncident
        fields = [
            'incident_type',
            'title',
            'description',
            'guest',
            'room',
            'action_taken',
        ]


class BlacklistRecordForm(forms.ModelForm):
    class Meta:
        model = BlacklistRecord
        fields = [
            'person_type',
            'full_name',
            'phone',
            'reason',
        ]


class KeyCardLogForm(forms.ModelForm):
    class Meta:
        model = KeyCardLog
        fields = [
            'room',
            'guest',
            'action',
            'note',
        ]


class PatrolLogForm(forms.ModelForm):
    class Meta:
        model = PatrolLog
        fields = [
            'area_checked',
            'observation',
            'issue_found',
        ]