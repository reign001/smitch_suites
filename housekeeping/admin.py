from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    RoomCleaning,
    LaundryRequest,
    LostAndFound,
    MaintenanceIssue
)

admin.site.register(RoomCleaning)
admin.site.register(LaundryRequest)
admin.site.register(LostAndFound)
admin.site.register(MaintenanceIssue)