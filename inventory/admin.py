from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import InventoryCategory, Supplier, InventoryItem, StockIn, StockOut, DepartmentRequest


admin.site.register(InventoryCategory)
admin.site.register(Supplier)
admin.site.register(InventoryItem)
admin.site.register(StockIn)
admin.site.register(StockOut)
admin.site.register(DepartmentRequest)