from django.contrib import admin
from .models import Product , Variation

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('product_name',)}
    list_display = ['id','product_name','price','stock','slug','created_date','modified_date','is_available']
    list_display_links = ['id']
class VariationAdmin(admin.ModelAdmin):
    list_display = ['id' ,'product' , 'variation_category' , 'variation_value','is_active' ]
    list_editable = ['is_active',]
    list_filter = ['id' ,'product' , 'variation_category' , 'variation_value', ]
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
