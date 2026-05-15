from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import GuestCRMProfile, GuestComplaint, GuestFeedback, CorporateClient

admin.site.register(GuestCRMProfile)
admin.site.register(GuestComplaint)
admin.site.register(GuestFeedback)
admin.site.register(CorporateClient)