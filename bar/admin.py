from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import BarItem, BarSale, BarSaleItem

admin.site.register(BarItem)
admin.site.register(BarSale)
admin.site.register(BarSaleItem)