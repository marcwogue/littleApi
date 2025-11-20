from django.contrib import admin
from .models import MenuItem
from .models import User
from .models import Order
from .models import CartItem
from .models import OrderItem
# Register your models here.

admin.site.register(MenuItem)
admin.site.register(User)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)


