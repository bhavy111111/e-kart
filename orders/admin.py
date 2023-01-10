from django.contrib import admin

# Register your models here.
from .models import Order , Payment , OrderProduct
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user']

#admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(OrderProduct)
