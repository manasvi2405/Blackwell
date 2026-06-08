from django.contrib import admin
from .models import Cart,CartItem,UserProfile,Address,Order,OrderItem

# Register your models here.
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)