from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MenuItem, MenuItemIngredient, RestaurantOrder, RestaurantOrderItem

admin.site.register(MenuItem)
admin.site.register(MenuItemIngredient)
admin.site.register(RestaurantOrder)
admin.site.register(RestaurantOrderItem)