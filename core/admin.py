from django.contrib import admin
from core.models import Product, Category, Supplier, ProductReview,CartOrder,CartOrderItems,Wishlist,ContactMessage


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'product_image', 'price', 'category','supplier', 'product_status','created_at')
    list_filter = ('category','supplier','product_status')
    search_fields = ('title','category__title','supplier_name')

  
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','title',) 
    search_fields = ('title',)


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'area', 'contact')
    list_filter = ('area',)
    search_fields = ('name', 'area')


class CartOrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','get_total_price','paid_status','order_date','product_status')
    list_filter = ('paid_status','product_status',)
    search_fields = ('user__username',)
    list_editable = ('paid_status','product_status',)

    def get_total_price(self, obj):
        return obj.price  

    get_total_price.short_description = "Total Price"
    
class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ('id','order','item','qty','price','total')
    search_fields = ('order__id','item')

  
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id','get_username','product','review','rating','get_review_date')
    list_filter = ('rating',)
    search_fields = ('product__title', 'user__username')
    def get_review_date(self, obj):
        return obj.date 
    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = "User"

    get_review_date.short_description = "Review Date"

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id','user','product')



class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'option','short_message','created_at', 'is_replied')
    list_filter = ('is_replied', 'created_at')
    search_fields = ('name', 'email', 'message')

    def short_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    short_message.short_description = "Message"


   

admin.site.register(Product,ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(CartOrder,CartOrderAdmin)
admin.site.register(CartOrderItems,CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)

admin.site.register(Wishlist,WishlistAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)


