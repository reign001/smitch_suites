from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Room, Guest, Booking, CheckIn, CheckOut, Payment, RoomServiceRequest, GuestCharge


admin.site.register(Room)
admin.site.register(Guest)
admin.site.register(Booking)
admin.site.register(CheckIn)
admin.site.register(CheckOut)
admin.site.register(Payment)
admin.site.register(RoomServiceRequest)
admin.site.register(GuestCharge)